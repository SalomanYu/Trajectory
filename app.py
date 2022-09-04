#!/usr/bin/python3.10

import re
from way import Way
import config
import os
from rich.console import Console


def build_way(professions_path: str):
    tablename = re.sub("\d+ ", "", professions_path).replace(" ", '_').replace(",", "").replace('.xlsx', '')
    # print(tablename)
    my_way = Way(professions_db=os.path.join(config.PROFESSIONS_FOLDER_PATH, professions_path), db_tablename=tablename, logging_dir=ex_file.replace(".xlsx", ''))
    my_way.parse_current_profession()
    # my_way.collect_data_from_sql_to_json()
    # my_way.remove_repeat_groupes()
    # my_way.rename_to_default_names()
    # my_way.join_reset_steps()
    # my_way.detect_profession_experience_time()

    # снова возвращаемся к 5 и 6 шагу
    # my_way.join_reset_steps(logfile="step_5_2.log", dataPath=config.JSONFILE.STEP_6.value)
    # my_way.detect_profession_experience_time(logfile="step_6_2.log")

    # my_way.find_similar_workWays()
    # my_way.connect_steps()



if __name__ == "__main__":
    console = Console()

    for ex_file in os.listdir(path=config.PROFESSIONS_FOLDER_PATH):
        if ex_file.endswith(".xlsx"):
            if ex_file == "39 Инвестиции, ценные бумаги и управление финансами.xlsx":
                print("работаем с файлом профессий: ", ex_file)
                build_way(professions_path=ex_file)
                break
