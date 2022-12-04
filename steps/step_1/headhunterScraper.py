import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from loguru import logger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import settings.database as database
from settings.config import ProfessionStep, ExcelProfession, HH_VARIABLES
from steps.step_1.resumeScraper import ResumeScraper



class Scraper:
    def __init__(self, profession: ExcelProfession):
        logger.info(f"Начали работать с профессией {profession}")
        self.profession = profession
        self.domain = "https://hh.ru"
        self.activePage = 1
        self.pageStep = 1
        self.POOLS = 10

    def run(self):
        professionUrl = self.__search_profession()
        self.__pagination_by_profession_search(professionUrl)

    def __search_profession(self) -> str:
        """Вернет ссылку на результат поиска. Далее эта ссылка будет принименяться в пагинации"""
        logger.info(f"Запустили поиск по профессии: {self.profession.name}")
        SEARCH_URL = 'https://hh.ru/employer?hhtmFrom=resume_search_result'

        options = Options()
        options.add_argument("--headless") # Фоновый режим
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        web = webdriver.Chrome(options=options)
        web.get(SEARCH_URL)
        web.implicitly_wait(5)

        searchInput = web.find_element(By.XPATH, "//input[@class='search-input--l5LJ0qBrszPOtQDqE96I']")
        searchInput.click()
        searchInput.send_keys(self.profession.name)
        searchInput.send_keys(Keys.ENTER)
        web.implicitly_wait(5)

        professionUrl = web.current_url
        web.quit()
        return professionUrl


    def __pagination_by_profession_search(self, professionUrl: str) -> ...:
        logger.info(f"Результат поиска: {professionUrl}")
        soup = self.__get_soup(professionUrl)
        lastPageNum = soup.find_all("span", class_='pager-item-not-in-short-range')[-1].find("a",class_='bloko-button')
        if not lastPageNum:return

        for page in range(int(lastPageNum.text)):
            logger.info(f"Page num: {page}")
            if self.__parse_current_resumes(pageUrl=f"{professionUrl}&page={page}") is None: break
        
        for page in range(int(lastPageNum.text)):
            logger.info(f"Page num: {page}")
            if self.__parse_current_resumes(pageUrl=f"{professionUrl}?page={page}") is None: break



    def __parse_current_resumes(self, pageUrl: str):
        currentResumes = self.__find_current_resumes(pageUrl)
        if not currentResumes: 
            logger.warning(f"На этой странице нет подходящих профессий: {pageUrl}")
            return False
        logger.success(f"Нашли на странице {len(currentResumes)} подходящих профессий: {pageUrl}")

        with Pool(self.POOLS) as process:
            process.map_async(
                func=self.parse_resume,
                iterable=currentResumes,
                error_callback = lambda x: logger.error(f"Thread error:[{x}]"))
            process.close()
            process.join()
        return True


    def __find_current_resumes(self, pageUrl: str) -> set[tuple[str, str]]:
        currentResumes: set[tuple[str, str]] = set() # Будем хранить ссылку и дату обновления, т.к больше нигде дату не взять

        soup = self.__get_soup(pageUrl)
        # Проверяем на какой странице находимся
        try:
            currentPage = int(soup.find('span', class_='bloko-button bloko-button_pressed').text)
            if currentPage != self.activePage: raise AttributeError
        except AttributeError: 
            logger.info(f"Страница не найдена: {pageUrl}")
            return None
        self.activePage += self.pageStep
        
        resumeInPage = soup.find("div", class_="resume-serp")
        # print(resumeInPage)
        for resume in resumeInPage:
            title = resume.find("a", class_="serp-item__title")
            if title.text.lower().strip() == self.profession.name.lower().strip():
                resumeUrl = self.domain + title['href']
                try: 
                    dateUpdate = resume.find("span", class_='date--cHInIjOdiyfDqTabYRkp').text.replace("Обновлено", "").replace(u"\xa0", u" ")
                except:
                    logger.warning(f"Не удалось получить ДАТУ ОБНОВЛЕНИЯ: {pageUrl}") 
                    dateUpdate = ""
                currentResumes.add((resumeUrl, dateUpdate))
        
        return currentResumes
    

    def __get_soup(self, url: str) -> BeautifulSoup:
        try:
            req = requests.get(url, headers=HH_VARIABLES.headers)
        except BaseException as err:
            logger.error(f"Не удалось отправить запрос по адресу: {url}\nТекст ошибки:{err}")
        soup = BeautifulSoup(req.text, 'lxml')
        return soup


    def parse_resume(self, resumeUrlWithDateUpdate: tuple[str, str]):
        resumeData: list[ProfessionStep] = self.__collectInfoAboutResume(resumeUrlWithDateUpdate)
        logger.success("Спарсили резюме")
        database.add(table_name='smm', data=resumeData, db_name="Data/SQL/10.2022/Parser.db")
        logger.success("Добавли в БД")

    def __collectInfoAboutResume(self, resumeUrlWithDateUpdate: tuple[str, str]) -> list[ProfessionStep]:
        professionSteps : list[ProfessionStep] = []
        url, dateUpdate = resumeUrlWithDateUpdate
        soup = self.__get_soup(url)

        resume = ResumeScraper(soup)
        title = resume.get_title()
        salary = resume.get_salary()
        skills = resume.get_skills()
        city = resume.get_city()
        univer = resume.get_education_info()
        training = resume.get_training()
        languages = resume.get_languages()
        specializations = resume.get_specializations()
        experience_term = resume.get_experience_term()
        workPeriods = resume.get_experience(url)

        for work in workPeriods:
            professionSteps.append(ProfessionStep(title, work.post, work.interval, work.duration, work.branch, work.subbranch,
                    self.profession.weight_in_group, self.profession.level, self.profession.weight_in_level, self.profession.groupID,
                    self.profession.area, city, experience_term, specializations, salary, univer.name, univer.direction,
                    univer.year, languages, skills, training.name, training.direction, training.year, dateUpdate, url))
        return professionSteps	

