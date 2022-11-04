#!/usr/bin/python3.10

import re
from way import Way
import settings.config as config
import os
from rich.console import Console
from settings.tools import group_steps_to_resume
import settings.database as database

def save_final_result_to_db(similared_workways: list[config.ResumeGroup]) -> None:
    database.clear_table('New')
    
    for resume in similared_workways:
        for step in resume.ITEMS:
            database.add(table_name='New', data=step)

def build_way(professions_path: str):
    """Метод создает экземпляр класса Way и запускает поэтапное построение траектории"""

    tablename = re.sub("\d+ ", "", professions_path).replace(" ", '_').replace(",", "").replace('.xlsx', '')
    my_way = Way(professions_db=os.path.join(config.PROFESSIONS_FOLDER_PATH, professions_path), db_tablename=tablename, logging_dir=professions_path.replace(".xlsx", ''))
    my_way.parse_current_profession()
    exit('Закончили парсинг')
    # my_way.collect_data_from_sql_to_json()
    # Поменять аргументы на переменные
    # change_structure_table_in_sql(old_db="Data/SQL/9.2022/Security.db", old_table="Охрана_и_безопасность",new_table="охрана_и_безопасность")
    # resumes_without_duplicates = my_way.remove_repeat_groupes()
    resumes = group_steps_to_resume(database.get_all_resumes(table_name='New', db_name='Data/SQL/10.2022/Way — копия.db'))
    resumes_without_repeat_steps = my_way.join_reset_steps(resumes)
    updated_resumes = my_way.detect_profession_experience_time(resumes_without_repeat_steps)    
    # # # снова возвращаемся к 5 и 6 шагу
    # resume = group_steps_to_resume(database.get_all_resumes(table_name='New'))

    resumes_without_repeat_steps = my_way.join_reset_steps(resumes_without_duplicates=updated_resumes)
    updated_resumes = my_way.detect_profession_experience_time(resumes_without_repeat_steps)

    similared_workways = my_way.find_similar_workWays(updated_resumes)
    database.save_final_result_to_db(similared_workways)
    # my_way.connect_steps()


def start():
    """Метод ищет в папке с профессиями все эксель-файлы и по ним начинает строить траектории"""
    for ex_file in os.listdir(path=config.PROFESSIONS_FOLDER_PATH):
        if ex_file.endswith(".xlsx"):
            # Тестируем для одного файла
            if ex_file == "161 Ит _ Интернет _ Телеком.xlsx":
                print("работаем с файлом профессий: ", ex_file)
                build_way(professions_path=ex_file)
                break


if __name__ == "__main__":    
    import time
    st = time.monotonic()
    start()
    end = time.monotonic()
    print(f"Время: {end-st}")
