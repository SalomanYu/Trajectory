"""Основной файл, который будет вызывать этапы построения траектории один за другим"""

import os
from rich.progress import track

import settings.tools as tools
import settings.config as config
import settings.database as database

from steps.step_1.parserProfession import ProfessionParser
import steps.step_3.removeRepeatResumes as step_3
import steps.step_5.joinRepeatStepsInResume as step_5
import steps.step_6.renameZeroLevelProfession as step_6
import steps.step_7.joinSimilarTrajectories as step_7
import steps.step_7.addition as step_7_addition
import steps.step_8.connectionBetweenSteps as step_8

import steps.visual.vizualization as vizual

# OLD_DB_NAME = "Data/SQL/10.2022/Vetirenar.db"
# OLD_TABLE_NAME = "Ветеринария"
# NEW_TABLE_NAME = "Vet"

class Way:
    """Класс, содержащий логику вызовов каждого этапа. Каждый метод класса подготавливает необходимые
    для работы этапа данные и передает их ему"""


    def __init__(self, professions_db: str, db_tablename:str, logging_dir: str):
        """Вроде как db_tablename не нужен """
        self.professions_db = professions_db
        self.logging_dir = logging_dir
        self.db_table_name = db_tablename.replace(".", "_").lower() # В названии таблицы не должно быть точек
        self.db_table_name = 'New'


    def parse_current_profession(self) -> None:
        """Парсим актуальные резюме из hh.ru"""

        log = tools.start_logging(logfile="step_1.log", folder=self.logging_dir)
        excel_data = tools.get_professions_from_excel(path=self.professions_db)
        for item in track(range(len(excel_data)), description="[yellow]Profession parsing progress"):
            prof_item = excel_data[item] 
            self.db_table_name = prof_item.area
            log.debug("Searching profession - %s", prof_item.name)

            profession = ProfessionParser(
                name_db_table=self.db_table_name,
                profession_name=prof_item.name,
                profession_area=prof_item.area,
                profession_level=prof_item.level,
                profession_weight_in_group=prof_item.weight_in_group,
                profession_weight_in_level=prof_item.weight_in_level,
                profession_groupID=prof_item.groupID
            )
            profession.find()
        print("Step 1 finished!")
    
    def remove_repeat_groupes(self) -> list[config.ResumeGroup]:
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
        resumes = database.get_all_resumes(table_name=self.db_table_name)
        grouped_resumes = tools.group_steps_to_resume(resumes)

        groups, duplicate_list = step_3.filtering_groups(log, grouped_resumes)
        data_without_duplicates = step_3.remove_dublicates(log=log, data=groups, list_to_delete=duplicate_list)
        print("Step 3 finished!")
        return data_without_duplicates

    def join_reset_steps(self, resumes_without_duplicates: list[config.ResumeGroup], 
        logfile: str = "step_5.log") -> list[config.ResumeGroup]:
        """Метод склеивает между собой два и более повторяющихся этапа, если у них одинаковое название
        и одинаковая отрасль. После склеивания одному из методов присваевается общий опыт двух
        этапов и соответственно меняется промежуток работы.
        После чего второй этап подлежит удалению"""

        log = tools.start_logging(logfile=logfile, folder=self.logging_dir)
        resumes, duplicate_set = step_5.join_steps(log=log, data=resumes_without_duplicates)
        resumes_without_repeat_steps = step_5.remove_repeat_steps(log=log, data=resumes, set_to_remove=duplicate_set)
        print("Step 5 finished!")
        return resumes_without_repeat_steps
    

    def detect_profession_experience_time(self, resumes_without_repeat_steps: list[config.ResumeGroup],
        logfile: str = "step_6.log") -> list[config.ResumeGroup]:
        """Метод занимается переименованием должностей и профессий нулевого уровня. Т.к после этого метода
         высока вероятность появления новых дубликатов среди этапов карьеры, то следует после этого метода снова вызывать предыдущий.
         Но передавать в качестве вводных данных уже измененные этим методом данные. Т.к у нас будут новые объединения этапов, нам нужно снова
         прогнать метод определения среднего опыта и переименования должностей согласно этим данным"""

        log = tools.start_logging(logfile=logfile, folder=self.logging_dir)
        areas = database.get_all_areas(tablename='New')
        default_names, edwica_db_names = tools.get_default_names(areas)
        profession_statistic = step_6.get_average_duration(resumes=resumes_without_repeat_steps)
        corrected_statistic = step_6.corrent_min_interval_between_levels(data=profession_statistic)
        # vizual.show_vizualization_step_6(default_names=default_names, statistic=corrected_statistic)
        renamed_zero_professions = step_6.rename_zero_professions_by_experience(
            log=log, 
            resumes=resumes_without_repeat_steps, 
            default_names=default_names,
            profession_default_values=corrected_statistic,
            edwica_db_names=edwica_db_names)
        print("Step 6 finished!")
        return renamed_zero_professions


    def find_similar_workWays(self, renamed_zero_professions: list[config.ResumeGroup]):
        log = tools.start_logging("step_7.log", folder=self.logging_dir)
        # Объединение путей 
        similared_steps = step_7.detect_similar_workWays(log, renamed_zero_professions)    
        
        # Визуализация
        # data_7 = tools.load_resumes_json(log, config.STEP_7_JSON_FILE, True)
        # data_3 = tools.load_resumes_json(log, config.STEP_3_JSON_FILE, False)
        # vizual.show_step_7(data_3, data_7)

        # Дополнение
        # print(step_7_addition.ind_most_popular_workWay(log=log))
        print("Step 7 finished!")
        return similared_steps


    def connect_steps(self):
        step_8.create_table()
        log = tools.start_logging(logfile="step_8.log", folder=self.logging_dir)
        data = tools.load_resumes_json(log=log, path=config.JSONFILE.STEP_7.value, is_seven_step=True)

        connection_between_steps = step_8.find_connection_between_steps(resumes=data)
        for item in track(range(len(connection_between_steps)), description='[yellow]Запись в БД'):
            step_8.add_to_table(data=connection_between_steps[item])

        # vizual.vizual_connect_between_steps(data, resumes=data)
 