"""Основной файл, который будет вызывать этапы построения траектории один за другим"""

import os
from rich.progress import track

import tools
import config

from steps.step_1_parse_current_profession import ProfessionParser
from steps.step_2_collected_data import SelectData
import steps.step_3_remove_repeat_groupes as step_3
import steps.step_4_rename_to_default_name as step_4
import steps.step_5_join_reset_steps_in_career as step_5
import steps.step_6_zero_proffession_rename as step_6
import steps.step_7_join_similar_trajectories as step_7
import steps.step_7_2_addition as step_7_addition
import steps.step_8_connect_between_steps as step_8

import steps.step_vizualization as vizual


class Way:
    def __init__(self, professions_db: str, db_tablename:str, logging_dir: str):
        self.professions_db = professions_db
        self.logging_dir = logging_dir
        self.db_table_name = db_tablename


    def parse_current_profession(self) -> None:
        """"""

        log = tools.start_logging(logfile="step_1.log", folder=self.logging_dir)
        excel_data = tools.connect_to_excel(path=self.professions_db)
        # console.log("[green] Start parsing professions")
        for item in track(range(len(excel_data.names)), description="[yellow]Profession parsing progress"):
            log.debug("Searching profession - %s", excel_data.names[item])
            
            self.db_table_name = excel_data.area
            profession = ProfessionParser(
                name_db_table=self.db_table_name,
                profession_name=excel_data.names[item],
                profession_area=excel_data.area,
                profession_level=excel_data.levels[item],
                profession_weight_in_group=excel_data.weights_in_group[item],
                profession_weight_in_level=excel_data.weights_in_level[item]
            )
            profession.find()
        print("Step 1 finished!")


    def collect_data_from_sql_to_json(self) -> None:
        """Метод существует исключительно для удобной работы разработчика, который хотел поработать с json-файлами. В идеале нужно отказаться от этого метода
        И производить все операции с данными в SQL-формате"""

        log = tools.start_logging(logfile="step_2.log", folder=self.logging_dir)
        collector = SelectData(
            db_path=os.path.join("SQL", config.CURRENT_MONTH, config.DATABASE_NAME),
            db_table=self.db_table_name,
            file_output_name=config.STEP_2_JSON_FILE,
            log=log
        )
        collector.collect()
        print("Step 2 finished!")

    
    def remove_repeat_groupes(self) -> None:
        """Метод удаляет одинаковые резюме (называется группой, т.к в БД представляет собой совокупность строк) в БД\n
        Резюме считается дубликатом, если встречается резюме у которого:\n
        1.Одинаковое наименование резюме\n
        2.Одинаковое количество этапов\n
        3.Совпадение по наименованиям в каждой должности\n
        4.Совпадение по отрасли в каждой должности\n
        5.Одинаковый стаж\n

        Если хотя бы 4 из этих пунктов не прошли проверку или не прошли проверку все пункты, кроме первого (различное написание резюме),
        то резюме (группа) считается дубликатом и удаляется
        """

        log = tools.start_logging(logfile="step_3.log", folder=self.logging_dir)
        data = tools.load_resumes_json(log, path=config.STEP_2_JSON_FILE)
        # data = tools.load_table_data_from_database(tablename=config.DatabaseTable.STEP_2.value)
        groups, duplicate_list = step_3.filtering_groups(log, data)
        data_without_duplicates = step_3.remove_dublicates(log=log, data=groups, list_to_delete=duplicate_list)
        tools.save_resumes_to_json(log=log, resumes=data_without_duplicates, filename=config.STEP_3_JSON_FILE)
        # tools.save_resumes_to_database(data=data_without_duplicates, tablename=config.DatabaseTable.STEP_3.value)
        print("Step 3 finished!")


    def rename_to_default_names(self):
        """В предшествущих версиях Технологии построения путей этот пункт имел право на жизнь. 
        Хотя сейчас его скорее всего можно удалить в угоду производительности"""
        
        log = tools.start_logging("step_4.log", folder=self.logging_dir)
        step_4.set_resume_names_to_default_values(log, path=self.professions_db)
        print("Step 4 finished!")

    
    def join_reset_steps(self, logfile: str = "step_5.log", dataPath: str = config.STEP_4_JSON_FILE, is_seven_step: bool = False):
        """Метод склеивает между собой два повторяющихся этапа, если у них одинаковое название и одинаковая отрасль
        После склеивания одному из методов присваевается общий опыт двух этапов и соответственно меняется промежуток работы.
        После чего второй этап подлежит удалению"""

        log = tools.start_logging(logfile=logfile, folder=self.logging_dir)
        data = tools.load_resumes_json(log=log, path=dataPath, is_seven_step=is_seven_step)
        resumes, duplicate_set = step_5.join_steps(log=log, data=data)
        resumes_without_duplicate_steps = step_5.remove_repeat_steps(log=log, data=resumes, set_to_remove=duplicate_set)
        tools.save_resumes_to_json(log=log, resumes=resumes_without_duplicate_steps, filename=config.STEP_5_JSON_FILE)

        print("Step 5 finished!")
    

    def detect_profession_experience_time(self, logfile: str = "step_6.log"):
        """Метод занимается переименованием должностей и профессий нулевого уровня. Т.к после этого метода
         высока вероятность появления новых дубликатов среди этапов карьеры, то следует после этого метода снова вызывать предыдущий.
         Но передавать в качестве вводных данных уже измененные этим методом данные. Т.к у нас будут новые объединения этапов, нам нужно снова
         прогнать метод определения среднего опыта и переименования должностей согласно этим данным"""

        log = tools.start_logging(logfile=logfile, folder=self.logging_dir)
        resumes = tools.load_resumes_json(log=log, path=config.STEP_5_JSON_FILE)
        
        default_names, edwica_db_names = tools.get_default_names(profession_excelpath=self.professions_db)
        profession_statistic = step_6.get_average_duration(resumes=resumes)
        corrected_statistic = step_6.corrent_min_interval_between_levels(data=profession_statistic)
        # vizual.show_vizualization(default_names=default_names, statistic=corrected_statistic)
        step_6.rename_zero_professions_by_experience(log=log, resumes=resumes, default_names=default_names, profession_default_values=corrected_statistic,edwica_db_names=edwica_db_names)
        print("Step 6 finished!")


    def find_similar_workWays(self):
        log = tools.start_logging("step_7.log", folder=self.logging_dir)
        # Объединение путей 
        data = tools.load_resumes_json(log, config.STEP_6_JSON_FILE)
        step_7.detect_similar_workWays(log, data)    
        
        # Визуализация
        # data_7 = tools.load_resumes_json(log, config.STEP_7_JSON_FILE, True)
        # data_3 = tools.load_resumes_json(log, config.STEP_3_JSON_FILE, False)
        # vizual.show_step_7(data_3, data_7)

        # Дополнение
        # print(step_7_addition.find_most_popular_workWay(log=log))

        print("Step 7 finished!")


    def connect_steps(self):
        step_8.create_table()
        log = tools.start_logging(logfile="step_8.log", folder=self.logging_dir)
        data = tools.load_resumes_json(log=log, path=config.STEP_7_JSON_FILE, is_seven_step=True)

        # connection_between_steps = step_8.find_connection_between_steps(resumes=data)
        # for item in track(range(len(connection_between_steps)), description='[yellow]Запись в БД'):
        #     step_8.add_to_table(data=connection_between_steps[item])

        vizual.vizual_connect_between_steps(data='', resumes=data)
 