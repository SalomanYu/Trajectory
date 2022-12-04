"""Основной файл, который будет вызывать этапы построения траектории один за другим"""

from rich.progress import track
from loguru import logger
import settings.tools as tools
import settings.config as config
import settings.database as database

from steps.step_1.headhunterScraper import Scraper
import steps.step_2.removeRepeatResumes as step_2
import steps.step_3.joinRepeatStepsInResume as step_3
import steps.step_4.renameZeroLevelProfession as step_4
import steps.step_5.joinSimilarTrajectories as step_5
import steps.step_6.connectionBetweenSteps as step_6


class Way:
    """Класс, содержащий логику вызовов каждого этапа. Каждый метод класса подготавливает необходимые
    для работы этапа данные и передает их ему"""


    def __init__(self, professions_db: str, logging_dir: str):
        """Вроде как db_tablename не нужен """
        self.professions_db = professions_db
        self.logging_dir = logging_dir
        self.db_table_name = 'New'

        logger.remove() # Запрещаем выводить сообщения в терминал
        logger.add("Data/LOGGING/way.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", mode="w")


    def parse_current_profession(self) -> None:
        """Парсим актуальные резюме из hh.ru"""
        excel_data = tools.get_professions_from_excel(path=self.professions_db)
        for item in track(range(len(excel_data)), description="[yellow]Profession parsing progress"):
            prof_item = excel_data[item] 
            scraper = Scraper(prof_item)
            scraper.run()
        logger.debug("Step 1 finished!")
    
    def remove_repeat_groupes(self, resumes: list[config.ResumeGroup]) -> list[config.ResumeGroup]:
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
        logger.debug("Шаг: Начали очищать резюме от повторяющихся этапов в карьере")
        # resumes = database.get_all_resumes(table_name=self.db_table_name)
        # grouped_resumes = tools.group_steps_to_resume(resumes)

        groups, duplicate_list = step_2.filtering_groups(resumes)
        data_without_duplicates = step_2.remove_dublicates(data=groups, list_to_delete=duplicate_list)
        logger.debug("Step 2 finished!")
        return data_without_duplicates

    def join_reset_steps(self, resumes_without_duplicates: list[config.ResumeGroup]) -> list[config.ResumeGroup]:
        """Метод склеивает между собой два и более повторяющихся этапа, если у них одинаковое название
        и одинаковая отрасль. После склеивания одному из методов присваевается общий опыт двух
        этапов и соответственно меняется промежуток работы.
        После чего второй этап подлежит удалению"""

        resumes, duplicate_set = step_3.merge_all_resumes_steps(resumes_without_duplicates)
        resumes_without_repeat_steps = step_3.remove_repeat_steps(data=resumes, set_to_remove=duplicate_set)
        logger.debug("Step 3 finished!")
        return resumes_without_repeat_steps
    

    def detect_profession_experience_time(self, resumes_without_repeat_steps: list[config.ResumeGroup]) -> list[config.ResumeGroup]:
        """Метод занимается переименованием должностей и профессий нулевого уровня. Т.к после этого метода
         высока вероятность появления новых дубликатов среди этапов карьеры, то следует после этого метода снова вызывать предыдущий.
         Но передавать в качестве вводных данных уже измененные этим методом данные. Т.к у нас будут новые объединения этапов, нам нужно снова
         прогнать метод определения среднего опыта и переименования должностей согласно этим данным"""

        areas = database.get_all_areas(tablename='parsed', db_name="Data/SQL/11.2022/IT.db")
        default_names, edwica_db_names = tools.get_default_names(areas)
        profession_statistic = step_4.get_average_duration(resumes=resumes_without_repeat_steps)
        corrected_statistic = step_4.corrent_min_interval_between_levels(data=profession_statistic)
        renamed_zero_professions = step_4.rename_zero_professions_by_experience(
            resumes=resumes_without_repeat_steps, 
            default_names=default_names,
            profession_default_values=corrected_statistic,
            edwica_db_names=edwica_db_names)
        logger.debug("Step 4 finished!")
        return renamed_zero_professions


    def find_similar_workWays(self, renamed_zero_professions: list[config.ResumeGroup]) -> list[config.ResumeGroup]:
        # Объединение путей 
        similared_steps = step_5.detect_similar_workWays(renamed_zero_professions)    
        logger.debug("Step 5 finished!")
        return similared_steps

    def connect_steps(self, resumes: list[config.ResumeGroup]):
        step_6.create_table()

        connection_between_steps = step_6.find_connection_between_steps(resumes)
        for item in track(range(len(connection_between_steps)), description='[yellow]Запись в БД'):
            step_6.add_to_table(data=connection_between_steps[item])

        # vizual.vizual_connect_between_steps(data, resumes=data)
 