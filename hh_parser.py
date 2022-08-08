"""Основной парсер для сбора информации о всех наименованиях резюме.
Парсер ориентируется на город соискателя и категорию"""

import re
import os
import time
import sqlite3
import requests 

from bs4 import BeautifulSoup
from datetime import date
from multiprocessing import Pool

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from settings import HH_VARIABLES, Experience, ResumeItem, Training, University, WorkExperience, CurrentSearchItem
from settings import logging
import settings


class Resume:
    def __init__(self):
        self.page_url = None
        self.city = None
        self.name_db_table = 'Resumes'
        self.name_database = HH_VARIABLES.name_db
        self.cities = HH_VARIABLES.cities
        self.parsing_urls = HH_VARIABLES.parsing_urls
        self.headers = HH_VARIABLES.headers

    def start(self):
        """Основная функция, которая осуществляет переход по всем городам и категориям"""
        
        self.create_table(self.name_db_table)

        for self.city in self.cities: # Отбираем каждый город из списка по отдельности
            
            for item in range(len(self.parsing_urls)): # Запускаем цикл по отфильтрованным по ссылкам категории
                logging.info("City, were are finding - %s", self.city)
                # Этот цикл отвечает за перелистывание страниц
                url = f'https://{self.city}.hh.ru' + self.parsing_urls[item].url
                for page_num in range(250): # 250
                    self.page_url = f"{url}&page={page_num}"
                    self.parser_resume_list(self.page_url)

    def parser_resume_list(self, url: str) -> list:
        """Метод будет запускать парсинг нескольких резюме в многопотоке
        Принимает: url - это ссылка из пагинатора хх.ру, в котором представленно 20 ссылок на резюме
        """

        try: # Пробуем подключиться к странице пагинатора
            req = requests.get(url, headers=self.headers) # открываем страницу со списком резюме
            soup = BeautifulSoup(req.text, 'lxml')
    
            # Создаем список ссылок всех резюме
            resume_urls_list = [f"https://{self.city}.hh.ru{item['href']}" for item in soup.find_all('a', class_='resume-search-item__name')]        
            logging.info("Started four processes for parsing")
            with Pool(4) as process:
                process.map_async(  func=self.parse_resume, # Функция, которая будет вызываться с аргументом
                                    iterable=resume_urls_list, # Список аргументов, которые будут передаваться по очереди
                                    error_callback=lambda x:logging.error('Thread error --> %s', x) # Что будет, если произодет ошибка в многоптоке
                )
                process.close()
                process.join()
            return resume_urls_list
        except requests.exceptions.ConnectionError:
            logging.error("Internet-connection failed.")            
            logging.debug("Let`s try to connect in two minute")            
            time.sleep(120)

    def parse_resume(self, resume: CurrentSearchItem) -> tuple:
        """Функция запускает методы парсинга отдельных блоков резюме и передает результат в виде списка или списка кортежей функции data_resume_list"""

        url, self.resume_dateUpdate = resume
        print(f"{self.resume_dateUpdate}")
        logging.info('Parsing resume...')
        try:
            self.req = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(self.req.text, 'lxml')
            
            data = self.collect_all_resume_info(soup, url) # Мы передаем soup и затем переопределяем его, чтобы из-за многопоточности не было смешиваний резюме
            try:
                if isinstance(data[0], tuple): # Условие необходимо для резюме, у которых несколько мест работы. Поэтому они возвращают список с кортежами строк для записи в БД
                    self.add_to_table(self.name_db_table, data, many_rows=True)
                    # print('Записали в таблицу инфу о списке резюме')
                else: # Здесь строки записываются по одному
                    self.add_to_table(self.name_db_table, data)
                
            except BaseException as error:
                logging.error('Failed to write resume in database... (%s)', url)
            return 
            
        except BaseException as error:
            logging.error('Failed to parse resume. Problem: %s. Resume url - %s', error, url)
            return []

    def collect_all_resume_info(self, soup: BeautifulSoup, url: str) -> ResumeItem | list[ResumeItem]:
        """Метод собирает все методы парсера в один массив данных"""

        experience, work_periods  = self.get_experience(soup, url)        
        univer = self.get_education_info(soup)
        specializations = self.get_specialization(soup)
        training = self.get_training(soup)
        languages = self.get_languages(soup)
        self.salary = self.get_salary(soup)
        key_skills = self.get_skills(soup)
        title = self.get_title(soup)
        
                
        if len(work_periods) > 0:
            res = []
            for work in work_periods: # Пробегаемся по количеству мест работы 
                res.append(ResumeItem(name=title, city=self.city, 
                                general_experience=experience, specialization=specializations, salary=self.salary,
                                university_name=univer.name, university_direction=univer.direction, university_year=univer.year,
                                languages=languages, skills=key_skills, training_name=training.name, training_direction=training.direction,
                                training_year=training.year, branch=work.branch, subbranch=work.subbranch, experience_interval=work.interval,
                                experience_duration=work.duration, experience_post=work.post, url=url))
            return res 
        else: # Вариант, когда нет опыта работы
            return  ResumeItem(name=title, city=self.city, 
                                general_experience=experience, specialization=specializations, salary=self.salary,
                                university_name=univer.name, university_direction=univer.direction, university_year=univer.year,
                                languages=languages, skills=key_skills, training_name=training.name, training_direction=training.direction,
                                training_year=training.year, branch='', subbranch='', experience_interval='', experience_duration='', 
                                experience_post='', url=url)


    def get_title(self, soup: BeautifulSoup) -> str:
        """Метод получения наименования резюме"""
     
        try:
            self.soup = soup
            title = self.soup.find(attrs={'data-qa': 'resume-block-title-position', 'class': 'resume-block__title-text'}).text
        
            return title
        except BaseException as error:
            logging.warning("Has no NAME")
            return ''

    def get_salary(self, soup: BeautifulSoup) -> str:
        """Метод получения зарплаты резюме"""

        try:
            self.soup = soup
            salary = self.soup.find('span', class_='resume-block__salary resume-block__title-text_salary')

            if salary:
                return salary.text
            else: 
                return ''
        except BaseException as error:
            logging.warning("Has no SALARY")
            return ''

    def get_specialization(self, soup: BeautifulSoup) -> str:
        try:
            self.soup = soup
            specializations =  [item.text for item in self.soup.find_all('li', class_='resume-block__specialization')] # Забираем перечень специализаций
            return " | ".join(specializations)
        except BaseException as error:
            logging.warning("Has no SPECIALIZATION")
            return ''


    def get_education_info(self, soup: BeautifulSoup) -> University:
        """Метод получения информации об образовании"""
        self.soup = soup
        try:
            # переменная нужна, чтобы понять указано ли учебное заведение в описании образования или нет
            education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(class_='bloko-header-2').text 
            
            # список всех учебных заведений
            educations_list = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', class_='resume-block-item-gap').find_all('div', class_='resume-block-item-gap')
            if len(educations_list) > 0: 
                education_names_list = []
                education_directions_list = []
                education_years_list = []
                for item in educations_list:
                    name = item.find(attrs={'data-qa':'resume-block-education-name'}).text 
                    # Тут прописывается проверка указано ли направление образования или нет. Обычно направления нет у тех, кто оканчивал только школу
                    direction = '' if item.find(attrs={'data-qa':'resume-block-education-organization'}) == None else item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                    year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                    
                    education_names_list.append(name)
                    education_directions_list.append(direction)
                    education_years_list.append(year)

                return  University(name=' | '.join(education_names_list), direction=' | '.join(education_directions_list), year=' | '.join(education_years_list))
            
            else: # Если в разделе Образование написано просто - среднее образование
                if education_type == 'Образование':
                    education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find_all('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-9 bloko-column_l-12')[-1].text
                    return University(name=education_type, direction='', year='')

        except BaseException as error:
            logging.warning("Has no EDUCATION")
            return  University(name='', direction='', year='')

    def get_skills(self, soup: BeautifulSoup) -> str:
        """Метод получения информации о навыках """
        
        try:
            self.soup = soup
            if self.soup.find('div', class_='bloko-tag-list') != None: # Проверяем существует ли блок с навыками соискателя
                skills_html = self.soup.find('div', class_='bloko-tag-list').find_all('span')
                key_skills = []
                for item in skills_html:
                    key_skills.append(item.text)
                return ' | '.join(key_skills) if type(key_skills) == list else key_skills

            else:
                return ''
        except AttributeError:
            logging.warning("Has no SKILLS")
            return ''

    def get_languages(self, soup: BeautifulSoup) -> str:
        """Метод получения информации о доступных языках"""

        try:
            self.soup = soup
            languages = [item.text for item in self.soup.find(attrs={'data-qa': 'resume-block-languages'}).find_all('p')]
            edited_languages = []
            for language in languages:
                new_lang = language.split('—')[0] + f"({language.split(' — ')[1]})" # Приводим к виду [ Русский ( Родной); Английский ( B2 — Средне-продвинутый) ]
                edited_languages.append(new_lang)

            return " | ".join(edited_languages)
        except BaseException as error:
            logging.warning("Has no LANGUAGES")
            return ''

    def get_experience(self, soup, url) -> Experience:
        """Метод получения информации об опыте работы"""
        
        try:
            self.soup = soup
            work_soup = self.soup # Потребуется для изменения soup внутри функции во время вызова selenium

            work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'})
            self.work_periods = set()
            if work_spaces == None:
                self.experience = Experience(global_experience='', work_places={
                    WorkExperience(post='', interval='', branch='', subbranch='', duration='')
                    })
                return self.experience
            else:
                if work_soup.find('span', class_='resume-industries__open'):
                    options = Options()
                    options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    
                    browser = webdriver.Chrome(options=options)
                    browser.get(url)
                    browser.implicitly_wait(3)

                    see_more_btns = browser.find_elements(By.XPATH, "//span[@class='resume-industries__open']")
                    for btn in see_more_btns: btn.click()     
                    work_soup = BeautifulSoup(browser.page_source, 'lxml') # Переопределение soup`a 
                    work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'}) # Переопределение опыта                
                    browser.quit()


                self.total_work_experience = work_soup.find('span', class_='resume-block__title-text resume-block__title-text_sub').text
                if  'опыт работы' in self.total_work_experience.lower():
                    self.total_work_experience = self.total_work_experience.replace(u'\xa0', u' ').replace('Опыт работы', '')
                elif 'work experience' in self.total_work_experience.lower():
                    self.total_work_experience = self.total_work_experience.replace(u'\xa0', u' ').replace('Work experience', '')
                else:
                    self.total_work_experience = work_soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[1].text.replace(u'\xa0', u' ').replace('Опыт работы', '')

                
                for work in work_spaces.find_all('div', class_='resume-block-item-gap')[1:]:
                    pattern_period = '\w+ \d{4} — \w+ \d{4}' # найдет все записи следующего вида: Июнь 2005 — Февраль 2021

                    period = work.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text.replace(u'\xa0', u' ')
                    period_new = re.findall(pattern_period, period)[0] if re.findall(pattern_period, period) else re.findall('\w+ \d{4} — .*?\d', period)[0][:-1]
                    
                    months_count = re.split(pattern_period, period)
                    if len(months_count) > 1:
                        months_count = months_count[-1]
                    else:
                        months_count = re.findall('\d+', re.findall('\w+ \d{4} — .*?\d+', period)[0].split()[-1])[-1] +  ' '.join(re.split('\w+ \d{4} — .*?\d+', period))

                    work_title = work.find('div', {'data-qa':'resume-block-experience-position',"class":'bloko-text bloko-text_strong'}).text
                    try:
                        branch = [item.text for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('p')]
                        subranches = []
                        # Следующий цикл для подотраслей такого типа: https://kazan.hh.ru/resume/8bbd526100027d2f200039ed1f323563626552?hhtmFrom=resume_search_result
                        for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('ul'):
                            subranches.append(' ; '.join([li.text for li in item.find_all('li')]))
                    except BaseException:
                        branch = [work.find('div', class_='resume-block__experience-industries resume-block_no-print').text.split('...')[0]]
                        subranches = []
                    self.work_periods.add(WorkExperience(
                        post=work_title, interval=period_new, duration=months_count, branch=" | ".join(branch), subbranch=" | ".join(subranches))
                        )
            return Experience(global_experience=self.total_work_experience, work_places=self.work_periods)
        except BaseException as error:
            logging.warning("Has no WORK EXPERIENCE")
            self.experience = Experience(global_experience='', work_places={
                    WorkExperience(post='', interval='', branch='', subbranch='', duration='')
                    })
            return self.experience

    def get_training(self, soup: BeautifulSoup) -> Training:
        """Метод получения информации о повышении квалификации"""

        try:
            self.soup = soup
            training_html = self.soup.find('div', attrs={'data-qa': 'resume-block-additional-education', 'class':'resume-block'}).find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap')
            if len(training_html) > 0:
                education_names_list = []
                education_directions_list = []
                education_years_list = []
                for item in training_html:
                    year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                    company = item.find(attrs={'data-qa':'resume-block-education-name'}).text
                    direction = item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                    
                    education_names_list.append(company)
                    education_directions_list.append(direction)
                    education_years_list.append(year)
                return Training(
                    name=" | ".join(education_names_list),
                    direction=" | ".join(education_directions_list),
                    year=" | ".join(education_years_list)
                )
            else:
                raise BaseException
        except BaseException:
            logging.warning("Has no COURSES")
            return Training(name='', direction='', year='')

    
    def connect_to_db(self, db_name: str) -> settings.Connection:
        """Метод подключения к существующей БД
        Принимает: название БД"""
       
        self.db_name = db_name
        today = date.today()
        month_folder = f'SQL/{str(today.month)}.{str(today.year)}' # For history check
        os.makedirs(month_folder, exist_ok=True) # Создаем папку SQL, если она еще не создана

        # Будет создана База данных, если в папке SQL не будет файла db_name.db
        db = sqlite3.connect(f'{month_folder}/{self.db_name}') 
        cursor = db.cursor()
        return cursor, db
        
    def create_table(self, name: str) -> None:
        """Метод, который создает таблицы внутри БД для хранения всей информации о резюме
        Принимает: название таблицы"""
        
        cursor, db = self.connect_to_db(self.name_database)
        # Создание необходимых колонок
        pattern = f"""
            CREATE TABLE IF NOT EXISTS {name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_of_profession VARCHAR(255),
                city VARCHAR(50),
                general_experience VARCHAR(50),
                specialization VARCHAR(255),
                salary VARCHAR(50),
                higher_education_university TEXT,
                higher_education_direction TEXT,
                higher_education_year VARCHAR(100),
                languages VARCHAR(255),
                skills TEXT,
                advanced_training_name TEXT,
                advanced_training_direction TEXT,
                advanced_training_year VARCHAR(100),
                branch VARCHAR(255),
                subbranch VARCHAR(255),
                experience_interval VARCHAR(50),
                experience_duration VARCHAR(50),
                experience_post VARCHAR(255),
                url VARCHAR(255)
                );
            """
        cursor.execute(pattern)
        db.commit()
        db.close()

    def add_to_table(self, name:str, data:ResumeItem | list[ResumeItem], many_rows: bool=False) -> None:
        """Метод умеет добавлять в БД как и одну строку, так и несколько строк сразу
        Отличия в том, что резюме с несколькими строками означает, что в резюме
        указано несколько мест работы и для удобства их нужно разместить на разных строках"""
        cursor, db = self.connect_to_db(self.name_database)
        pattern = f"INSERT INTO {name}(name_of_profession, city, general_experience, specialization, salary, higher_education_university,"\
                    "higher_education_direction, higher_education_year, languages, skills, advanced_training_name, advanced_training_direction," \
                    f"advanced_training_year, branch, subbranch, experience_interval, experience_duration, experience_post, url) VALUES({','.join('?' for i in range(20))})"

        if many_rows:
            cursor.executemany(pattern, data) # Результат выполнения команды в скобках VALUES превратится в VALUES(?,?,?, ?n), n = len(data)
        else:
            cursor.execute(pattern, data)
 
        db.commit()
        db.close()
        if isinstance(data, list):
            logging.info("%s - added to database.", data[0].name)
        else:
            logging.info("%s - added to database.", data.name)

if __name__ == "__main__":  
    bot = Resume()
    bot.start()
