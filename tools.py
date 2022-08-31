import logging
import os
import json
import xlrd
import re
from datetime import datetime

from config import *


def start_logging(logfile: str="logfile.log", folder:str="undetinfied") -> logging:
    """Метод будет ввести журналирование траектории.
    Для каждого этапа будет создан отдельный файл. Для каждой профессии будет создана своя папка
    Логирование будет хранить ежемесячную историю изменений"""
    folder_path = os.path.join("LOGGING", CURRENT_MONTH, folder)
    os.makedirs(folder_path, exist_ok=True)
    logfile_path = os.path.join(folder_path, logfile)
    log_file = open(logfile_path, 'w') 
    log_file.close()

    logging.basicConfig(filename=logfile_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING) # Без этого urllib3 выводит страшные большие белые сообщения
    logging.getLogger('selenium').setLevel(logging.WARNING)
    return logging


def load_resumes_json(log:logging, path:str, is_seven_step:bool = False) -> list[ResumeGroup]:
    """Метод будет собирает данные из json-файлов и будет их выдавать
    в удобном виде списка с элементами представляющими тип данных ResumeGroup"""
    File = open(path)
    data = json.load(File)
    File.close()

    log.info(f"Took json-data from {path}")

    if is_seven_step:
        resumes = []
        for key, value in data.items():
            items = [ProfessionWithSimilarResumes(resume=DBResumeProfession(*tuple(resume.values())[:-1]), similar_id=tuple(resume.values())[-1]) for resume in value]
            resumes.append(ResumeGroup(ID=key, ITEMS=items))
    else: resumes = [ResumeGroup(ID=key, ITEMS=[DBResumeProfession(*resume.values()) for resume in value]) for key, value in data.items()]
    return resumes


def save_resumes_to_json(log: logging, resumes:list[ResumeGroup] | list[ProfessionWithSimilarResumes], filename: str, is_seven_step: bool = False) -> None:
    os.makedirs('JSON', exist_ok=True)
    """Метод, сохраняющий список элементов типа ResumeGroup"""
    res = {}
    if is_seven_step:
        for item in resumes:
            res[item.resume.ID] = []
            for elem in item.resume.ITEMS:
                res[item.resume.ID].append(dict(zip(JSONFIELDS + ["similar_path_ID"], [*elem]+[item.similar_id]))) # если мы на этапе объединения похожих путей, то добавляем еще одну графу
    
    else:
        for resume in resumes:
            res[resume.ID] = []
            for item in resume.ITEMS:
                res[resume.ID].append(dict(zip(JSONFIELDS, [*item])))
    
    with open(filename, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    log.info("%s saved to JSON!", filename)


def save_to_json(log:logging, data:list[dict], filename:str) -> None:
    os.makedirs('JSON', exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    log.info("%s saved!", filename)


def connect_to_excel(path:str) -> ExcelData:
    """Метод возвращает список профессий определенных одним profession_ID"""
    profession_area = re.sub("\d+", '', path).split('/')[-1].split(".xlsx")[0].strip().replace(" ", '_')
    book_reader = xlrd.open_workbook(path)
    work_sheet = book_reader.sheet_by_name('Вариации названий')
    table_titles = work_sheet.row_values(0)
    
    for col_num in range(len(table_titles)):
        match table_titles[col_num]:
            case 'Наименование професии и различные написания':
                table_names = [name for name in work_sheet.col_values(col_num)[1:] if name != '']
            case 'Вес профессии в уровне':
                table_weight_in_level = [int(weight) for weight in work_sheet.col_values(col_num)[1:] if weight != '']
            case 'Вес профессии в соответсвии':
                table_weight_in_group = [int(weight) for weight in work_sheet.col_values(col_num)[1:] if weight != '']
            case 'Уровень должности':
                table_level = [int(level) for level in work_sheet.col_values(col_num)[1:] if level != '']
    return ExcelData(table_names, profession_area, table_weight_in_level, table_weight_in_group, table_level)


def connect_to_excel_222(path:str) -> ExcelProfession:
    """Метод возвращает список профессий определенных одним profession_ID"""
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
    for row in range(1, work_sheet.nrows):
        try: int(work_sheet.cell(row, groupID_col).value)
        except ValueError: 
            # print(f"Выход из метода connect_to_excel_222: [Ошибка] не проставлены ID группы для файла: {path}")
            return
        data.append(ExcelProfession(
            groupID=int(work_sheet.cell(row, groupID_col).value),
            name=work_sheet.cell(row, names_col).value,
            area=profession_area,
            level=int(work_sheet.cell(row, level_col).value),
            weight_in_group=int(work_sheet.cell(row, weight_in_group_col).value),
            weight_in_level=int(work_sheet.cell(row, weight_in_level_col).value)
        ))
    return data


def get_default_average_value(statistic:set, level:int) -> int:
    if statistic and sum(statistic) > 0: return round(sum(statistic) / len(statistic))
    else: return DEFAULT_VALUES[level]


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


def find_profession_in_proffessions_db(profession_name: str) -> str | None:
    for File in os.listdir(PROFESSIONS_FOLDER_PATH):
        if File.endswith(".xlsx"):
            professions = connect_to_excel_222(os.path.join(PROFESSIONS_FOLDER_PATH, File))
            if professions: 
                for prof in professions:
                    if prof.name.lower() == profession_name.lower().strip():
                        current_prof = find_default_name_for_profession(proff_dbPath=os.path.join(PROFESSIONS_FOLDER_PATH, File), level=prof.level, profID=prof.groupID)
                        return current_prof.name

    add_profession_to_unknownDB(profession=profession_name)


def find_default_name_for_profession(proff_dbPath: str, level: int, profID: int): # profID: int,
    professions = connect_to_excel_222(proff_dbPath)
    if professions:
        for prof in professions:
            if  level == prof.level and prof.weight_in_level == 1 and prof.groupID == profID :
                return prof
    
        # Если 
        for prof in professions:
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



def move_dbData_to_groups(data: list[DBResumeProfession]) -> dict:
    """Метод получает на вход результат парсера в виде списка, каждого строка которого представляет собой
    одно место работы соискателя. Чтобы собрать все этапы в одно резюме нам требуется этот метод"""

    data_groups = {}
    for item in data:
        resume = DBResumeProfession(*item)
        if resume.url in data_groups: data_groups[resume.url].append(dict(zip(JSONFIELDS, item)))
        else: data_groups[resume.url] = [dict(zip(JSONFIELDS, item))]
    
    return data_groups


def get_default_names(profession_excelpath: str) -> tuple[set[DefaultLevelProfession], list]:
    book_reader = xlrd.open_workbook(profession_excelpath)
    work_sheet = book_reader.sheet_by_name("Вариации названий")
    table_titles = work_sheet.row_values(0)

    for col_num in range(len(table_titles)):
        match table_titles[col_num]:
            case "Наименование професии и различные написания":
                table_names_col = col_num
            case "Вес профессии в уровне":
                table_weight_in_level_col = col_num
            case "Уровень должности":
                table_level_col = col_num
            case "Вес профессии в соответсвии":
                table_weight_in_group = col_num
            case "ID список профессий":
                table_groupID_col = col_num
    
    names = [item for item in work_sheet.col_values(table_names_col) if item != '']
    default_names = set()

    for row_num in range(work_sheet.nrows):
        # Это условие фильтрует профессии по 'Id список профессий'
        # Если кортежа с содержимым (айди профессии, уровень профессии) нет в таком же кортеже дефолтных значений, то добавляем профессию
        if (work_sheet.cell(row_num, table_groupID_col), work_sheet.cell(row_num, table_level_col) not in 
            ((default.profID, default.level) for default in default_names)):

            if (work_sheet.cell(row_num, table_weight_in_level_col).value == 0) and (work_sheet.cell(row_num, table_weight_in_group).value == 1):
                default_names.add(DefaultLevelProfession(
                    profID=int(work_sheet.cell(row_num, table_groupID_col).value), 
                    name=work_sheet.cell(row_num, table_names_col).value, 
                    level=int(work_sheet.cell(row_num, table_level_col).value)))
            
            elif work_sheet.cell(row_num, table_weight_in_level_col).value == 1:
                default_names.add(DefaultLevelProfession(
                    profID=int(work_sheet.cell(row_num, table_groupID_col).value), 
                    name=work_sheet.cell(row_num, table_names_col).value, 
                    level=int(work_sheet.cell(row_num, table_level_col).value)))
        
    return default_names, names

# def load_table_data_from_database(tablename: DatabaseTable, is_seven_step: bool = False) -> list[ResumeGroup] | list[ProfessionWithSimilarResumes]:
#     """Метод нужен для подключения к конкретной таблице БД по построению путей для получения доступа к информации
#     конкретного шага( каждая таблица = один шаг построения пути)"""

#     db = sqlite3.connect(CURRENT_DATABASE_NAME)
#     cursor = db.cursor()

#     data = cursor.execute(f"SELECT * FROM {tablename}").fetchall()
#     data_groups = move_dbData_to_groups(data)
    
#     if is_seven_step:
#         resumes = []
#         for key, value in data_groups.items():
#             items = [ProfessionWithSimilarResumes(resume=DBResumeProfession(*tuple(resume.values())[:-1]), similar_id=tuple(resume.values())[-1]) for resume in value]
#             resumes.append(ResumeGroup(ID=key, ITEMS=items))
#     else: resumes = [ResumeGroup(ID=key, ITEMS=[DBResumeProfession(*resume.values()) for resume in value]) for key, value in data_groups.items()]
    
#     return resumes


# def save_resumes_to_database(data: list[ResumeGroup] | list[ProfessionWithSimilarResumes], tablename: DatabaseTable, is_seven_step: bool = False) -> None:

#     db = sqlite3.connect(CURRENT_DATABASE_NAME)
#     cursor = db.cursor()

#     if is_seven_step: ...
#     else: 
#         for group in data:
#             for resume in group.ITEMS:
#                 cursor.execute(adding_to_db_template(tablename=tablename), [*resume])
#                 db.commit()
#     db.close()


if __name__ == "__main__":
    # print(connect_to_excel(path='/home/saloman/Documents/Edwica/Trajectory/Professions/23 Управление персоналом.xlsx'))
    # names = {"hr-специалист","hello", "world", "find", "me"}
    # for i in names:
        # find_profession_in_proffessions_db(i)
    
    print(find_profession_in_proffessions_db("Консультант по подбору персонала"))