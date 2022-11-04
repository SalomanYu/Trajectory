import logging
import os
import json
import xlrd
import re
from rich.progress import track
from datetime import datetime

from settings.config import *
import settings.database as database

def start_logging(logfile: str="logfile.log", folder:str="undetinfied") -> logging:
    """Метод будет ввести журналирование траектории.
    Для каждого этапа будет создан отдельный файл. Для каждой профессии будет создана своя папка
    Логирование будет хранить ежемесячную историю изменений"""
    folder_path = os.path.join("Data/LOGGING", CURRENT_MONTH, folder)
    os.makedirs(folder_path, exist_ok=True)
    logfile_path = os.path.join(folder_path, logfile)
    log_file = open(logfile_path, 'w') 
    log_file.close()

    logging.basicConfig(filename=logfile_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING) # Без этого urllib3 выводит страшные большие белые сообщения
    logging.getLogger('selenium').setLevel(logging.WARNING)
    return logging


<<<<<<< HEAD
# def load_resumes_json(log:logging, path:str, is_seven_step:bool = False) -> list[ResumeGroup]:
#     """Метод будет собирает данные из json-файлов и будет их выдавать
#     в удобном виде списка с элементами представляющими тип данных ResumeGroup"""
#     with open(path, 'r', encoding="utf-8") as input_file:
#         line = input_file.read()
#         data = json.loads(line)

#     log.info(f"Took json-data from {path}")

#     if is_seven_step:
#         resumes = []
#         for key, value in data.items():
#             items = [ProfessionWithSimilarResumes(resume=DBResumeProfession(*tuple(resume.values())[:-1]), similar_id=tuple(resume.values())[-1]) for resume in value]
#             resumes.append(ResumeGroup(ID=key, ITEMS=items))
#     else: resumes = [ResumeGroup(ID=key, ITEMS=[DBResumeProfession(*resume.values()) for resume in value]) for key, value in data.items()]
#     return resumes
=======
def load_resumes_json(log:logging, path:str, is_seven_step:bool = False) -> list[ResumeGroup]:
    """Метод будет собирает данные из json-файлов и будет их выдавать
    в удобном виде списка с элементами представляющими тип данных ResumeGroup"""
    with open(path, 'r', encoding="utf-8") as input_file:
        line = input_file.read()
        data = json.loads(line)

    log.info(f"Took json-data from {path}")

    if is_seven_step:
        resumes = []
        for key, value in data.items():
            items = [ProfessionWithSimilarResumes(resume=DBResumeProfession(*tuple(resume.values())[:-1]), similar_id=tuple(resume.values())[-1]) for resume in value]
            resumes.append(ResumeGroup(ID=key, ITEMS=items))
    else: resumes = [ResumeGroup(ID=key, ITEMS=[DBResumeProfession(*resume.values()) for resume in value]) for key, value in data.items()]
    return resumes
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f

def find_profession_excelFile_by_area(area: str) -> str | None:
    folder = "Data/Professions"
    for file in os.listdir(path=folder):
        if file.endswith('.xlsx'):
            book = xlrd.open_workbook(os.path.join(folder, file))
            sheet = book.sheet_by_name('Список профессий')
            table_titles = sheet.row_values(0)
            for index, value in enumerate(table_titles):
                if value == 'Профобласть': 
                    area_column = index

                    if area in (area for area in sheet.row_values(area_column)):
                        return os.path.join(folder, file)
            


<<<<<<< HEAD
def get_professions_from_excel(area: str = 'Ит / Интернет / Телеком', path: str = None) -> list[ExcelProfession]:
    """Метод возвращает список профессий определенных одним profession_ID"""
    if path is None: path = find_profession_excelFile_by_area(area)
=======
def get_professions_from_excel(area: str) -> list[ExcelProfession]:
    """Метод возвращает список профессий определенных одним profession_ID"""
    path = find_profession_excelFile_by_area(area)
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f
    profession_area = re.sub("\d+", '', path).split('/')[-1].split(".xlsx")[0].strip().replace(" ", '_')
    book_reader = xlrd.open_workbook(path)
    work_sheet = book_reader.sheet_by_name('Вариации названий')
    table_titles = work_sheet.row_values(0)
    
    for col_num in range(len(table_titles)):
        match table_titles[col_num]:
            case 'Наименование професии и различные написания':
                names_col = col_num
            case 'Вес профессии в уровне':
                weight_in_level_col = col_num
            case 'Вес профессии в соответсвии':
                weight_in_group_col = col_num
            case 'Уровень должности':
                level_col = col_num
            case "ID список профессий": 
                groupID_col = col_num    
    data = []
    for row in range(1, work_sheet.nrows): # В файле могут быть пропущены значения в строках, поэтому здесь есть блок try-except
        try: int(work_sheet.cell(row, groupID_col).value)
        except ValueError: 
<<<<<<< HEAD
            print(f"Выход из метода get_professions_from_excel: [Ошибка] не проставлены ID группы для файла: {path}")
=======
            # print(f"Выход из метода get_professions_from_excel: [Ошибка] не проставлены ID группы для файла: {path}")
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f
            return
        try:weight_in_group = int(work_sheet.cell(row, weight_in_group_col).value)
        except ValueError: weight_in_group = 0 # Значит пустое поле
        try: weight_in_level = int(work_sheet.cell(row, weight_in_level_col).value)
        except ValueError: weight_in_level = 0
            
        data.append(ExcelProfession(
            groupID=int(work_sheet.cell(row, groupID_col).value),
            name=work_sheet.cell(row, names_col).value,
<<<<<<< HEAD
            area=area,
=======
            area=profession_area,
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f
            level=int(work_sheet.cell(row, level_col).value),
            weight_in_group=weight_in_group,
            weight_in_level=weight_in_level
        ))
    return data


def experience_to_months(experience: str) -> int:
    """Метод получает информацию о стаже в виде [12 лет 7 месяцев ] и возвращает ее в виде количества месяцев [151]"""
    
    experience = re.sub(' +', ' ', experience) # обрезаем лишние пробелы
    month_pattern = '\d{2} м|\d{2} m|\d м|\d m' # Регулярка для нахождения месяца
    year_pattern = '\d{2} г|\d{2} y|\d г|\d y|\d{2} л|\d л' # Регулярка для нахождения года

    try: # Пробуем найти информацию о месяцах в стаже 
        months = int(re.findall(month_pattern, experience)[0].split(' ')[0])
    except IndexError:
        months = 0
    try: # Пробуем найти информацию о годах в стаже 
        years = int(re.findall(year_pattern, experience)[0].split(' ')[0])
    except IndexError:
        years = 0

    if years:
        return years * 12 + months
    else:
        return months


def find_profession_in_proffessions_db(profession_name: str, area:str) -> str | None:
    """По area мы поймем в каком файле нужно искать профессию"""
    professions = get_professions_from_excel(area)
    if professions: 
        for prof in professions:
            if prof.name.lower() == profession_name.lower().strip():
                current_prof = find_default_name_for_profession(proff_dbPath=area, level=prof.level, profID=prof.groupID)
                return current_prof.name

    add_profession_to_unknownDB(profession=profession_name)


def find_default_name_for_profession(area: str, level: int, profID: int):
    professions = get_professions_from_excel(area)
    if professions:
        for prof in professions: # проверяем является ли профессия главной в уровне
            if  level == prof.level and prof.weight_in_level == 1 and prof.groupID == profID :
                return prof
    
        for prof in professions: # Проверям является ли профессия главной в группе 
            if  level == prof.level  and prof.groupID == profID and prof.weight_in_group == 1:
                return prof


def add_profession_to_unknownDB(profession: str) -> None:
    os.makedirs("SQL", exist_ok = True)

    db = sqlite3.connect(f"SQL/{UNKNOWN_PROFESSIONS_PATH}")
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS unknown(
        profID INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255),
        load_time DATETIME)
        """)
    db.commit()

    cursor.execute("""INSERT INTO unknown(title, load_time) VALUES(?, ?)""", (profession, datetime.now()))
    db.commit()
    db.close()

    print(f"Профессия {profession} была добавлена в список неопознанных профессий")



<<<<<<< HEAD
# def move_dbData_to_groups(data: list[DBResumeProfession]) -> dict:
#     """Метод получает на вход результат парсера в виде списка, каждого строка которого представляет собой
#     одно место работы соискателя. Чтобы собрать все этапы в одно резюме нам требуется этот метод"""

#     data_groups = {}
#     for item in data:
#         resume = DBResumeProfession(*item)
#         if resume.url in data_groups: data_groups[resume.url].append(dict(zip(JSONFIELDS, item)))
#         else: data_groups[resume.url] = [dict(zip(JSONFIELDS, item))]
    
#     return data_groups

def get_default_names(areas: tuple[str]) -> tuple[set[DefaultLevelProfession], list[EdwicaProfession]]:
    files = (find_profession_excelFile_by_area(area) for area in areas)
    default_names: set[DefaultLevelProfession] = set()
    edwica_db_names: list[EdwicaProfession] = []
=======
def move_dbData_to_groups(data: list[DBResumeProfession]) -> dict:
    """Метод получает на вход результат парсера в виде списка, каждого строка которого представляет собой
    одно место работы соискателя. Чтобы собрать все этапы в одно резюме нам требуется этот метод"""

    data_groups = {}
    for item in data:
        resume = DBResumeProfession(*item)
        if resume.url in data_groups: data_groups[resume.url].append(dict(zip(JSONFIELDS, item)))
        else: data_groups[resume.url] = [dict(zip(JSONFIELDS, item))]
    
    return data_groups

def get_default_names(areas: tuple[str]) -> tuple[set[DefaultLevelProfession], list[str]]:
    files = (find_profession_excelFile_by_area(area) for area in areas)
    default_names: set[DefaultLevelProfession] = set()
    edwica_db_names: list[str] = []
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f

    for profession_excelpath in files: # Интерируемся по каждому файлу, чтобы у нас в списке были все профобласти
        book_reader = xlrd.open_workbook(profession_excelpath)
        work_sheet = book_reader.sheet_by_name("Вариации названий")
        area_sheet = book_reader.sheet_by_name('Список профессий')        

        names_col = 6 # Наименование професии и различные написания
        weight_in_level_col = 5 # Вес профессии в уровне
        level_col = 4 # Уровень должности
        weight_in_group_col = 3 # Вес профессии в соответсвии
        groupID_col = 1 # ID список профессий
<<<<<<< HEAD
        area: str = [i for i in area_sheet.col_values(2)][1] # Выбираем профобласть        
        names: list[EdwicaProfession] = [EdwicaProfession(item, area) for item in work_sheet.col_values(names_col) if item != ''][1:] # Собираем все Наименования профессии и различные написания в переменную names
        edwica_db_names += names

=======
        names: list[str] = [item for item in work_sheet.col_values(names_col) if item != ''][1:] # Собираем все Наименования профессии и различные написания в переменную names
        area: str = [i for i in area_sheet.col_values(2)][1] # Выбираем профобласть        
        
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f
        # Ищем для каждого уровня 
        for row_num in range(1, work_sheet.nrows): # Начинаем со второй строки, чтобы не брать заголовки столбцов:
            name = work_sheet.cell(row_num, names_col).value
            groupId = int(work_sheet.cell(row_num, groupID_col).value)
            level = int(work_sheet.cell(row_num, level_col).value)
            weight_in_level = int(work_sheet.cell(row_num, weight_in_level_col).value) if  work_sheet.cell(row_num, weight_in_level_col).value else 0
            weight_in_group = int(work_sheet.cell(row_num, weight_in_group_col).value) if work_sheet.cell(row_num, weight_in_group_col).value else 0
            # Это условие фильтрует профессии по 'Id список профессий'
            # Если кортежа с содержимым (айди профессии, уровень профессии, профобласть) нет в таком же кортеже дефолтных значений, то добавляем профессию
            if (groupId, level, area) not in ((default.profID, default.level, default.area) for default in default_names):
                if (weight_in_level == 0 and  weight_in_group == 1) or (weight_in_level == 1):
                    default_names.add(DefaultLevelProfession(groupId, level, name, area))
<<<<<<< HEAD

    return default_names, edwica_db_names

# def move_json_to_db(jsonfile: str = "_"):
#     table = "Бухгалтерия_и_налоги"
#     log = start_logging()
#     database.create_table(table_name=table)
#     data = load_resumes_json(log, path=jsonfile, is_seven_step=True)
#     for resume in data:
#         for item in resume.ITEMS:
#             step = item.resume
#             row = ProfessionStep(step.name, step.experience_post, step.experience_interval, step.experience_duration,
#                 step.branch, step.subbranch, step.weight_in_group, step.level, step.weight_in_level, step.groupID, step.area,
#                 step.city, step.general_experience, step.specialization, step.salary, step.university_name,
#                 step.university_direction, step.university_year, step.languages, step.skills, step.training_name, step.training_direction,
#                 step.training_year, step.dateUpdate, step.url, item.similar_id)
#             database.add(table_name=table, data=row)
=======
        edwica_db_names += names

    return default_names, edwica_db_names

def move_json_to_db(jsonfile: str = "_"):
    table = "Бухгалтерия_и_налоги"
    log = start_logging()
    database.create_table(table_name=table)
    data = load_resumes_json(log, path=jsonfile, is_seven_step=True)
    for resume in data:
        for item in resume.ITEMS:
            step = item.resume
            row = ProfessionStep(step.name, step.experience_post, step.experience_interval, step.experience_duration,
                step.branch, step.subbranch, step.weight_in_group, step.level, step.weight_in_level, step.groupID, step.area,
                step.city, step.general_experience, step.specialization, step.salary, step.university_name,
                step.university_direction, step.university_year, step.languages, step.skills, step.training_name, step.training_direction,
                step.training_year, step.dateUpdate, step.url, item.similar_id)
            database.add(table_name=table, data=row)
>>>>>>> a778614650c45e0ec0375650062ae509fb4c374f

def change_structure_table_in_sql(old_db: str, old_table: str, new_table: str, new_db: str = CURRENT_DATABASE_NAME):
    """Это временный метод, который помогает привести старую структуру БД к одному виду
    Мы берем данные, которые спарсились не в том порядке и переделываем так, как нам надо"""
    database.create_table(new_table)
    db, cursor = database.connect(old_db)
    cursor.execute(f"SELECT * FROM {old_table}")

    data = (ResumeProfessionItem(*item[1:]) for item in cursor.fetchall())
    for step in data:
        row = ProfessionStep(step.name, step.experience_post, step.experience_interval, step.experience_duration,
                step.branch, step.subbranch, step.weight_in_group, step.level, step.weight_in_level, step.groupID, step.area,
                step.city, step.general_experience, step.specialization, step.salary, step.university_name,
                step.university_direction, step.university_year, step.languages, step.skills, step.training_name, step.training_direction,
                step.training_year, step.dateUpdate, step.url, similarPathId=0)
        database.add(table_name=new_table, data=row, db_name=new_db)

    db.close()

def group_steps_to_resume(data: tuple[ProfessionStep]) -> list[ResumeGroup]:
    resume_dict = {} # Вида ID-ссылка на резюме:list[ProfessionsStep]
    for step in data:
        if step.resumeId not in resume_dict:
            resume_dict[step.resumeId] = [step]
        else:
            resume_dict[step.resumeId].append(step)
    result = [ResumeGroup(ID=id, ITEMS=group) for id, group in resume_dict.items()] # Генератор нельзя использовать, т.к собираемся обращаться по индексу
    return result





if __name__ == "__main__":
    # print(connect_to_excel(path='/home/saloman/Documents/Edwica/Trajectory/Professions/23 Управление персоналом.xlsx'))
    # names = {"hr-специалист","hello", "world", "find", "me"}
    # for i in names:
        # find_profession_in_proffessions_db(i)
    
    print(find_profession_in_proffessions_db("Консультант по подбору персонала"))