import json
import sqlite3
import os
import logging

import settings
from settings import Connection, ResumeProfessionItem, ResumeGroup, start_logging


class SelectData:
    def __init__(self, db_path: str, db_table: str, file_output_name: str, log: logging):
        self.path = db_path
        self.db_table = db_table
        self.file_output_name = file_output_name
        self.log = log

    def collect(self) -> None:
        """Основной метод, который запускает все остальные функции"""
        data = self.select_all_rows()
        groups = self.group_user_ids_to_dict(data)
        settings.save_to_json(log=self.log, data=groups, filename=self.file_output_name)
        self.log.info("Complete!")

    def connect_to_db(self, path: str) -> Connection:
        try:
            if not os.path.exists(path):
                raise FileExistsError

            db = sqlite3.connect(path)
            cursor = db.cursor()
            self.log.info("Successfully connected to Database: %s", path)
            return Connection(cursor=cursor, db=db)

        except sqlite3.Error as error:
            self.log.error("Failed connecting to Database: %s", path)
            self.log.error("Error message: %s", error)
            exit("Failed connecting to Database")
        
        except FileExistsError:
            self.log.error("Database None-exists! %s", path)
            exit(f"[ERROR] Database None-exists: {path}")


    def select_all_rows(self) -> list[ResumeProfessionItem]:
        cur = self.connect_to_db(self.path).cursor
        cur.execute(f'SELECT * FROM {self.db_table}')

        resumes = [dict(zip(settings.JSONFIELDS, resume)) for resume in cur.fetchall()]
 
        return resumes
        

    def group_user_ids_to_dict(self, data: list[ResumeProfessionItem]) -> ResumeGroup:
        groups_dict = {}
        for row in data:
            url = row['user_id(url)']
            if url in groups_dict:
                is_repeat_resume = False
                for elem in groups_dict[url]:
                    if row['experience_interval'] == elem['experience_interval'] and row['experience_post'] == elem['experience_post']:
                        is_repeat_resume = True
                        break
                if not is_repeat_resume:
                    groups_dict[url].append(row)

            else:
                groups_dict[url] = [row]
        return groups_dict


if __name__ == "__main__":
    log = start_logging(logfile="step_2.log")
    collector = SelectData(
        db_path='/home/yunoshev/Documents/Edwica/Resumes/result_server/SQL/Professions(2022_6).dbcolle',
        file_output_name=settings.STEP_2_JSON_FILE,
        log=log
    )
    collector.collect()
