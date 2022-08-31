"""Данный файл является конфигурационным для траектории. Суть его в том, что здесь собраны все константы траектории и часто используемые функции"""

from datetime import date
import sqlite3

from enum import Enum
from typing import NamedTuple
from dataclasses import dataclass, astuple



PROFESSIONS_FOLDER_PATH = "Professions"
UNKNOWN_PROFESSIONS_PATH = "UnknownProfession.db" 
CURRENT_MONTH = f"{date.today().month}.{date.today().year}" # для истории создается папка с текущей датой
CURRENT_DATABASE_NAME = f"SQL/{CURRENT_MONTH}/Ammount.db"

DEFAULT_VALUES = { # Словарь стандартных значений для определения опыта в месяцах конкретного уровня [Уровень: значение в месяцах]
        1: 5,
        2: 12*3,
        3: 12*5,
        4: 12*50, # Пoставил 50, потому что в промежуток для среднего опыта сеньора может быть от 5 и выше
    }

@dataclass(frozen=True, slots=True) # Класс используемый в заголовках парсера. Его применение можно увидеть в конце файла в константе HEADERS
class RequiredUrls:
    category: str
    url: str

@dataclass
class DefaultExperience: # Используется в кортеже "стандартных уровни стажа работы"
    name: str
    level: int
    min_value: int
    max_value: int


@dataclass
class DBResumeProfession:
    db_id: int
    weight_in_group: int
    level: int
    weight_in_level: int
    area: str
    name: str
    city: str
    general_experience: str
    specialization: str
    salary: str
    university_name: str
    university_direction: str
    university_year: str | int
    languages: str
    skills: str
    training_name: str
    training_direction: str
    training_year: str
    branch: str
    subbranch: str
    experience_interval: str
    experience_duration: str
    experience_post: str
    dateUpdate: str
    url: str
    groupID: int

    def __iter__(self):
        return iter(astuple(self))

class ResumeProfessionItem(NamedTuple):
    weight_in_group: int
    level: int
    weight_in_level: int
    area: str
    name: str
    city: str
    general_experience: str
    specialization: str
    salary: str
    university_name: str
    university_direction: str
    university_year: str | int
    languages: str
    skills: str
    training_name: str
    training_direction: str
    training_year: str
    branch: str
    subbranch: str
    experience_interval: str
    experience_duration: str
    experience_post: str
    dateUpdate: str
    url: str


class ProfessionWithSimilarResumes(NamedTuple):
    resume: DBResumeProfession
    similar_id: int # общее число для обозначения индефикатора группы похожих резюме  

class ResumeGroup(NamedTuple): # Класс, который хранит информацию о резюме в виде айди резюме и списка разложенных этапов в карьере
    ID: str # Ссылка резюме
    ITEMS: tuple[ResumeProfessionItem] | tuple[ProfessionWithSimilarResumes]

class Variables(NamedTuple): # HH
    name_db: str
    cities: set['str']
    parsing_urls: set[RequiredUrls]
    headers: dict

class ExcelData(NamedTuple):
    names: tuple
    area: str
    weights_in_level: tuple
    weights_in_group: tuple
    levels: tuple

class ExcelProfession(NamedTuple):
    groupID: int
    name: str
    area: str
    weight_in_level: int
    weight_in_group: int
    level: int

class Training(NamedTuple): # Класс, хранящий информацию о пройденном курсе соискателя 
    name: str
    direction: str
    year: int

class University(NamedTuple): # Класс, хранящий информацию об образовании соискателя
    name: str
    direction: str
    year: int

class WorkExperience(NamedTuple): # Класс, хранящий информацию о каком либо этапе в карьере соискателя
    post: str # Product manager
    interval: str # Март 2017 — по настоящее время
    branch: str # Информационные технологии, системная интеграция, интернет
    subbranch: str # Разработка программного обеспечения
    duration: str # 5  лет 4 месяца

class Experience(NamedTuple): # Класс, хранящий информацию об общем опыте соискателя: стаж и множество этапов в карьере 
    global_experience: str # Например: 8 лет и 5 месяцев
    work_places: set[WorkExperience]

class Connection(NamedTuple): # Класс подключения к Базе данных
    cursor: sqlite3.Cursor
    db: sqlite3.Connection

class CurrentSearchItem(NamedTuple): # С помощью этого класса мы имеем возможность парсить полную информацию о резюме
    url: str # ссылка на подробное описание резюме
    dateUpdate: str # дата обновления - она находится здесь, потому что этой информаии нет на странице резюме. Мы можем брать ее только из поисковой выдачи hh.ru

class DefaultLevelProfession(NamedTuple): # Класс, позволяющий присвоить дефолтное наименование профессии для профессии с одинаковым ID и уровнем 
    profID: int
    level: int
    name: str

class LevelKeyWords(NamedTuple): # Класс, для хранения ключевых слов, определяющих уровень должности в карьере соискателя 
    level: int
    key_words: set

@dataclass
class LevelStatistic:
    name: str
    level: int
    value: int
    def __iter__(self):
        return iter(astuple(self))


class ProfessionStatistic(NamedTuple):
    prof_id: int
    levels: tuple[LevelStatistic]


class WorkWay(NamedTuple):
    post: str
    brach: str
    level: int
    
class ConnectionBetweenSteps(NamedTuple):
    job_title: str
    links: tuple[int]

class DatabaseTable(Enum):
    STEP_2 = "Управление_персоналом"
    STEP_3 = "NoneRepeatResumeDuplicates"
    STEP_4 = "ResumesByDefaultNames"
    STEP_5 = "ResumesWithoutStepsDuplicate"
    STEP_6 = "UpdateProfessionsWithZeroLevel"
    STEP_7 = "JoinSimilarWorkWaysBySimilarID"

class JSONFILE(Enum):
    STEP_2 = "JSON/step_2_groups_result.json"
    STEP_3 = "JSON/step_3_groups_without_duplicates.json"
    STEP_4 = "JSON/step_4_groups_with_default_names.json"
    STEP_5 = "JSON/step_5_groups_without_job_steps_duplicate.json"
    STEP_6 = "JSON/step_6_update_zero_levels.json"
    STEP_7 = "JSON/step_7_join_similar_path_by_similar_id.json"

# Данная константа помогает определить уровень должности по текущему на тот момент стажу. 
# Используется, когда у нас недостаточно данных для автоматического определения уровня 
# Измерения производятся в месяцах 
DEFAULT_LEVEL_EXPERIENCE = (
    DefaultExperience(name='intern', level=1, min_value=0, max_value=5),
    DefaultExperience(name='junior', level=2, min_value=6, max_value=36),
    DefaultExperience(name='middle', level=3, min_value=37, max_value=60),
    DefaultExperience(name='senior', level=4, min_value=61, max_value=999) # 999 заменяет выражение 'от 61 месяца и выше'
    ) 

# Кортеж с ключевыми словами для каждого уровня
LEVEL_KEYWORDS = (
    LevelKeyWords(level=1, key_words={'помощник', 'ассистент', 'стажёр', 'стажер', 'assistant', 'intern', 'интерн', 'волонтер', 'волонтёр'}),
    LevelKeyWords(level=2, key_words={'junior', 'младший', 'начинать', "начинаю"}), # начинающий заменен на начинать с учетом лемматизации
    LevelKeyWords(level=3, key_words={'middle', 'заместитель', 'старший', 'lead', 'ведущий', 'главный', 'лидер'}),
    LevelKeyWords(level=4, key_words={'senior', 'руководитель', 'head of', 'портфель', 'team lead', 'управлять', 'начальник', 'директор', 'head'})
    )
    
# Кортеж для объединения значений из БД с их заголовками. Используется для того
JSONFIELDS = [
    'id', 'weight_in_group', 'level', 'level_in_group', "area", 'name_of_profession', 'city', 'general_experience', 'specialization', 'salary', 
    'higher_education_university', 'higher_education_direction', 'higher_education_year', 'languages', 'skills', 'advanced_training_name', 'advanced_training_direction',
    'advanced_training_year', 'branch', 'subbranch', 'experience_interval', 'experience_duration', 'experience_post', "dateUpdate", 'user_id(url)', 'groupID']

HH_VARIABLES = Variables(
    name_db='HH_RU',
    cities={
        'kazan', 'spb', 'krasnodar', 'vladivostok', 'volgograd', 'voronezh', 'ekaterinburg', 'kaluga',
        'krasnoyarsk', 'rostov', 'samara', 'saratov', 'sochi', 'ufa', 'yaroslavl'
    },
    parsing_urls=(
        RequiredUrls(category='Admin_personal', url='/search/resume?professional_role=8&professional_role=33&professional_role=58&professional_role=76&professional_role=84&professional_role=88&professional_role=93&professional_role=110&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Safety', url='/search/resume?professional_role=22&professional_role=90&professional_role=95&professional_role=116&professional_role=120&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Top_management', url='/search/resume?professional_role=26&professional_role=36&professional_role=37&professional_role=38&professional_role=53&professional_role=80&professional_role=87&professional_role=125&professional_role=135&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Extraction_of_raw_materials', url='/search/resume?professional_role=27&professional_role=28&professional_role=49&professional_role=63&professional_role=79&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='IT', url='/search/resume?professional_role=10&professional_role=12&professional_role=25&professional_role=34&professional_role=36&professional_role=73&professional_role=96&professional_role=104&professional_role=107&professional_role=112&professional_role=113&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Art', url='/search/resume?professional_role=12&professional_role=13&professional_role=20&professional_role=25&professional_role=34&professional_role=41&professional_role=55&professional_role=98&professional_role=103&professional_role=139&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Marketing', url='/search/resume?professional_role=1&professional_role=2&professional_role=3&professional_role=10&professional_role=12&professional_role=34&professional_role=37&professional_role=55&professional_role=68&professional_role=70&professional_role=71&professional_role=99&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Medicine', url='/search/resume?professional_role=8&professional_role=15&professional_role=19&professional_role=24&professional_role=29&professional_role=42&professional_role=64&professional_role=65&professional_role=133&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Science', url='/search/resume?professional_role=17&professional_role=23&professional_role=79&professional_role=101&professional_role=132&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Sales', url='/search/resume?professional_role=6&professional_role=10&professional_role=51&professional_role=53&professional_role=54&professional_role=57&professional_role=70&professional_role=71&professional_role=83&professional_role=97&professional_role=105&professional_role=106&professional_role=121&professional_role=122&professional_role=129&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Production', url='/search/resume?professional_role=44&professional_role=45&professional_role=46&professional_role=48&professional_role=49&professional_role=63&professional_role=79&professional_role=80&professional_role=82&professional_role=85&professional_role=86&professional_role=109&professional_role=111&professional_role=115&professional_role=128&professional_role=141&professional_role=143&professional_role=144&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Consulting', url='/search/resume?professional_role=10&professional_role=75&professional_role=107&professional_role=134&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Personal_management', url='/search/resume?professional_role=17&professional_role=38&professional_role=69&professional_role=117&professional_role=118&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Accounting', url='/search/resume?professional_role=16&professional_role=18&professional_role=50&professional_role=134&professional_role=135&professional_role=136&professional_role=137&professional_role=142&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Lawyers', url='/search/resume?professional_role=145&professional_role=146&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Another', url='/search/resume?professional_role=40&relocation=living_or_relocation&gender=unknown&search_period=0')
    ),
    headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'})


adding_to_db_template = lambda tablename: f"""INSERT INTO {tablename} 
    (id, weight_in_group, level, level_in_group, area, name_of_profession, city, general_experience, specialization, salary, 
    higher_education_university, higher_education_direction, higher_education_year, languages, skills, advanced_training_name, advanced_training_direction,
    advanced_training_year, branch, subbranch, experience_interval, experience_duration, experience_post, dateUpdate, user_id, groupID)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """ # ?, count is 26
