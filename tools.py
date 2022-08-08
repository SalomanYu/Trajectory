import logging
import os
import json
import xlrd
import re
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

def load_resumes_json(log:logging, path:str) -> list[ResumeGroup]:
    """Метод будет собирает данные из json-файлов и будет их выдавать
    в удобном виде списка с элементами представляющими тип данных ResumeGroup"""
    File = open(path)
    data = json.load(File)
    File.close()

    log.info(f"Took json-data from {path}")
    resumes = [ResumeGroup(ID=key, ITEMS=[DBResumeProfession(*resume.values()) for resume in value]) for key, value in data.items()]
    return resumes

def save_resumes_to_json(log: logging, resumes:list[ResumeGroup], filename: str) -> None:
    os.makedirs('JSON', exist_ok=True)
    """Метод, сохраняющий список элементов типа ResumeGroup"""
    res = {}
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
            # case 'Профобласть':
                # table_area = work_sheet.col_values(col_num)[1]
            case 'Вес профессии в уровне':
                table_weight_in_level = [weight for weight in work_sheet.col_values(col_num)[1:] if weight != ''] # 25 Включительно
            case 'Вес профессии в соответсвии':
                table_weight_in_group = [weight for weight in work_sheet.col_values(col_num)[1:] if weight != '']
            case 'Уровень должности':
                table_level = [level for level in work_sheet.col_values(col_num)[1:] if level != '']
    return ExcelData(table_names, profession_area, table_weight_in_level, table_weight_in_group, table_level)

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