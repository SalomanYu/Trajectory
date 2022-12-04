import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from settings.config import University, Training, WorkExperience, Experience


class ResumeScraper:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def get_title(self) -> str:
        try: title = self.soup.find(attrs={'data-qa': 'resume-block-title-position', 'class': 'resume-block__title-text'}).text
        except BaseException as error: title = ''
        return title


    def get_salary(self) -> str:
        try:salary = self.soup.find('span', class_='resume-block__salary resume-block__title-text_salary').text
        except BaseException as error: salary = ''
        return salary


    def get_specializations(self) -> str:
        try: specializations =  (item.text for item in self.soup.find_all('li', class_='resume-block__specialization')) # Забираем перечень специализаций
        except BaseException as error: specializations = ()
        return " | ".join(specializations)


    def get_education_info(self) -> University:
        try:
            # переменная нужна, чтобы понять указано ли учебное заведение в описании образования или нет
            education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(class_='bloko-header-2').text 
            
            # список всех учебных заведений
            educations_list = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', class_='resume-block-item-gap').find_all('div', class_='resume-block-item-gap')
            if educations_list: 
                education_names_list: list[str] = []
                education_directions_list: list[str] = []
                education_years_list: list[str] = []
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
            return  University(name='', direction='', year='')


    def get_skills(self) -> str:
        try:
            if self.soup.find('div', class_='bloko-tag-list') is None: raise AttributeError # Проверяем существует ли блок с навыками соискателя
            else:
                skills_html = self.soup.find('div', class_='bloko-tag-list').find_all('span')
                key_skills: set[str] = set()
                for item in skills_html:
                    key_skills.add(item.text)
                return ' | '.join(key_skills)
        except AttributeError: return ''


    def get_languages(self) -> str:
        try:
            languages = [item.text for item in self.soup.find(attrs={'data-qa': 'resume-block-languages'}).find_all('p')]
            edited_languages: set[str] = set()
            for language in languages:
                new_lang = language.split('—')[0] + f"({language.split(' — ')[1]})" # Приводим к виду [ Русский ( Родной)| Английский ( B2 — Средне-продвинутый) ]
                edited_languages.append(new_lang)

            return " | ".join(edited_languages)
        except BaseException:
            return ''


    def get_city(self):
        city = self.soup.find('span', attrs={"data-qa": 'resume-personal-address'})
        return city.text


    def open_all_branches(self, url) -> BeautifulSoup:
        """Метод вебдрайвера, для нажатия на кнопки, чтобы посмотреть отрасли в опыте работы"""
        options = Options()
        options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        browser.implicitly_wait(3)
        see_more_btns = browser.find_elements(By.XPATH, "//span[@class='resume-industries__open']")
        for btn in see_more_btns: btn.click()     
        
        soup = BeautifulSoup(browser.page_source, 'lxml') # Переопределение soup`a 
        # work_spaces = soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'}) # Переопределение опыта                
        browser.quit()
        return soup


    def get_experience_term(self) -> str:
        """Стаж"""
        try:total_work_experience = self.soup.find('span', class_='resume-block__title-text resume-block__title-text_sub').text
        except: return ''

        if  'опыт работы' in total_work_experience.lower():
            total_work_experience = total_work_experience.replace(u'\xa0', u' ').replace('Опыт работы', '')
        elif 'work experience' in total_work_experience.lower():
            total_work_experience = total_work_experience.replace(u'\xa0', u' ').replace('Work experience', '')
        else:
            total_work_experience = self.soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[1].text.replace(u'\xa0', u' ').replace('Опыт работы', '')
        return total_work_experience


    def get_experience(self, url: str) -> list[WorkExperience]:
        """Метод получения информации об опыте работы"""
        
        try:
            experience_soup = self.soup
            work_periods: list[WorkExperience] = []
            work_spaces = experience_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'})
            
            if work_spaces is None:return [WorkExperience(post='', interval='', branch='', subbranch='', duration='')]
            else:
                if experience_soup.find('span', class_='resume-industries__open'):experience_soup = self.open_all_branches(url)
                work_spaces = experience_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'}) # Переопределяем переменную, чтобы сохранить туда отрасли      
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
                    work_periods.append(
                        WorkExperience(post=work_title, interval=period_new, duration=months_count, branch=" | ".join(branch), subbranch=" | ".join(subranches))
                        )
            return work_periods
        except BaseException:
            return [WorkExperience(post='', interval='', branch='', subbranch='', duration='')]


    def get_training(self) -> Training:
        """Метод получения информации о повышении квалификации"""
        try:
            training_html = self.soup.find('div', attrs={'data-qa': 'resume-block-additional-education', 'class':'resume-block'}).find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap')
            if not training_html: raise BaseException
            
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
                name=" | ".join(education_names_list), direction=" | ".join(education_directions_list), year=" | ".join(education_years_list))
        except BaseException:
            return Training(name='', direction='', year='')