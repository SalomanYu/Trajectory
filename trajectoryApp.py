"""Основной файл, который будет вызывать этапы построения траектории один за другим"""

import os
from rich.console import Console
from rich.progress import track

import settings
from steps.step_1_parse_current_profession import ProfessionParser
from steps.step_2_collected_data import SelectData
import steps.step_3_remove_repeat_groupes as step_3
import steps.step_4_rename_to_default_name as step_4
import steps.step_5_join_reset_steps_in_career as step_5
import steps.step_6_zero_proffession_rename as step_6
import steps.step_7_join_similar_trajectories as step_7


class Trajectory:
    def __init__(self, professions_db: str, logging_dir: str):
        self.professions_db = professions_db
        self.logging_dir = logging_dir
        self.db_table_name = "Маркетинг___Реклама____PR"

    def parse_current_profession(self) -> None:
        log = settings.start_logging(logfile="step_1.log", folder=self.logging_dir)
        excel_data = settings.connect_to_excel(path=self.professions_db)
        console.log("[green] Start parsing professions")
        for item in track(range(len(excel_data.names)), description="[yellow]HH.ru parser progress"):
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
        log = settings.start_logging(logfile="step_2.log", folder=self.logging_dir)
        collector = SelectData(
            db_path=os.path.join("SQL", settings.CURRENT_MONTH, settings.DATABASE_NAME),
            db_table=self.db_table_name,
            file_output_name=settings.STEP_2_JSON_FILE,
            log=log
        )
        collector.collect()
        print("Step 2 finished!")

    
    def remove_repeat_groupes(self):
        log = settings.start_logging(logfile="step_3.log", folder=self.logging_dir)
        data = settings.load_resumes_json(log, path=settings.STEP_2_JSON_FILE) # можно тоже заменить на меременную название файла
        groups, duplicate_list = step_3.filtering_groups(log, data)
        data_without_duplicates = step_3.remove_dublicates(log=log, data=groups, list_to_delete=duplicate_list)
        settings.save_resumes_to_json(log=log, resumes=data_without_duplicates, filename=settings.STEP_3_JSON_FILE)
        print("Step 3 finished!")


    def rename_to_default_names(self):
        log = settings.start_logging("step_4.log", folder=self.logging_dir)
        step_4.set_resume_names_to_default_values(log)
        print("Step 4 finished!")

    
    def join_reset_steps(self):
        log = settings.start_logging("step_5.log", folder=self.logging_dir)
        data = settings.load_resumes_json(log=log, path=settings.STEP_4_JSON_FILE)
        resumes, duplicate_set = step_5.join_steps(log=log, data=data)
        resumes_without_duplicate_steps = step_5.remove_repeat_steps(log=log, data=resumes, set_to_remove=duplicate_set)
        settings.save_resumes_to_json(log=log, resumes=resumes_without_duplicate_steps, filename=settings.STEP_5_JSON_FILE)

        print("Step 5 finished!")
    

    def detect_profession_experience_time(self):
        log = settings.start_logging("step_6.log", folder=self.logging_dir)
        resumes = settings.load_resumes_json(log=log, path=settings.STEP_5_JSON_FILE)
        default_names, edwica_db_names = step_4.get_default_names(profession_excelpath="Professions/43 Маркетинг _ Реклама. _ PR.xlsx")
        step_6.rename_zero_professions_by_experience(log=log, resumes=resumes, default_names=default_names, edwica_db_names=edwica_db_names)
        print("Step 6 finished!")

    def step_7(self):
        log = settings.start_logging("step_7.log", folder=self.logging_dir)
        data = settings.load_resumes_json(log, settings.STEP_6_JSON_FILE)
        step_7.detect_similar_trajectories(log, data)    
        print("Step 7 finished!")

    def step_8(self):
        pass
    

def create_trajectory(professions_path: str):
    trajectory = Trajectory(professions_db=os.path.join(settings.PROFESSIONS_FOLDER_PATH, professions_path), logging_dir=ex_file.replace(".xlsx", ''))
    # trajectory.parse_current_profession()
    trajectory.collect_data_from_sql_to_json()
    trajectory.remove_repeat_groupes()
    trajectory.rename_to_default_names()
    trajectory.join_reset_steps()
    trajectory.detect_profession_experience_time()
    trajectory.step_7()

if __name__ == "__main__":
    console = Console()

    for ex_file in os.listdir(path=settings.PROFESSIONS_FOLDER_PATH):
        if ex_file.endswith(".xlsx"):
            if ex_file == "43 Маркетинг _ Реклама. _ PR.xlsx":
                create_trajectory(professions_path=ex_file)
                break
    