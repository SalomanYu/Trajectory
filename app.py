#!/usr/bin/python3.10

from way import Way
import settings.config as config
import os
from settings.tools import group_steps_to_resume
import settings.database as database



def build_way(professions_path: str):
    """Метод создает экземпляр класса Way и запускает поэтапное построение траектории"""

    my_way = Way(professions_db=os.path.join(config.PROFESSIONS_FOLDER_PATH, professions_path), logging_dir=professions_path.replace(".xlsx", ''))
    my_way.parse_current_profession()
    # exit("Parsing stopped")
    # resumes = group_steps_to_resume(database.get_all_resumes(table_name='parsed', db_name='Data/SQL/11.2022/IT.db'))
    # my_way.remove_repeat_groupes(resumes)
    # resumes_without_repeat_steps = my_way.join_reset_steps(resumes)
    # updated_resumes = my_way.detect_profession_experience_time(resumes_without_repeat_steps)    
    
    # # снова возвращаемся к 5 и 6 шагу
    # resumes_without_repeat_steps = my_way.join_reset_steps(resumes_without_duplicates=updated_resumes)
    # updated_resumes = my_way.detect_profession_experience_time(resumes_without_repeat_steps)

    # similared_workways = my_way.find_similar_workWays(updated_resumes)
    # database.save_final_result_to_db(similared_workways)
    # my_way.connect_steps(similared_workways)


def start():
    """Метод ищет в папке с профессиями все эксель-файлы и по ним начинает строить траектории"""
    for ex_file in os.listdir(path=config.PROFESSIONS_FOLDER_PATH):
        if ex_file.endswith(".xlsx"):
            # Тестируем для одного файла
            if ex_file == "HR.xlsx":
                # print("работаем с файлом профессий: ", ex_file)
                build_way(professions_path=ex_file)
                break


if __name__ == "__main__":    
    import time
    st = time.monotonic()
    start()
    end = time.monotonic()
    print(f"Time: {end-st}")
