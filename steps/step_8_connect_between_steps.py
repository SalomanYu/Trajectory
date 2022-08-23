import os
from sys import getsizeof
import sqlite3
from rich.progress import track

from config import CURRENT_MONTH, ConnectionBetweenSteps, ResumeGroup, ProfessionWithSimilarResumes


def connect_to_db():
    folder = f"SQL/{CURRENT_MONTH}"
    os.makedirs(folder,  exist_ok=True)

    db = sqlite3.connect(f"{folder}/connect_between_steps.db")
    cursor = db.cursor()
    return db, cursor


def create_table():

    db, cursor = connect_to_db()
    cursor.execute("""CREATE TABLE IF NOT EXISTS job_posts(
        jobID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255),
        link TEXT
    )""")
    db.commit()
    db.close()


def add_to_table(data: ConnectionBetweenSteps) -> None:
    db, cursor = connect_to_db()
    cursor.execute("""INSERT INTO job_posts(name, link) VALUES(?, ?)""", (data.job_title, ",".join([str(i) for i in data.links])))
    
    db.commit()
    db.close()


def find_connection_between_steps(resumes: list[ResumeGroup] | list[ProfessionWithSimilarResumes]) -> set[ConnectionBetweenSteps]:
    # Почему то множества кушают больше памяти, чем списки
    # Разобраться почему так

    result = []
    used_steps = set()
    for current in track(range(len(resumes)), description='[green]Find connections between steps...'):
        current_job_steps = resumes[current].ITEMS
        for current_step in current_job_steps:
            if isinstance(current_step, ProfessionWithSimilarResumes): current_step = current_step.resume
            connections = []

            for comporable in range(current+1, len(resumes)):
                comporable_job_steps =  resumes[comporable].ITEMS
                for comporable_step in comporable_job_steps:    
                    if isinstance(comporable_step, ProfessionWithSimilarResumes): comporable_step = comporable_step.resume

                    if comporable_step.experience_post.lower() == current_step.experience_post.lower() and \
                    comporable_step.branch.lower() == current_step.branch.lower() and \
                    comporable_step.area.lower() == current_step.area.lower() and \
                    comporable_step.db_id not in used_steps:
                        
                        used_steps.add(comporable_step.db_id)
                        connections.append(comporable_step.db_id)

            result.append(ConnectionBetweenSteps(job_title=current_step.experience_post, links=tuple(connections)))

    del used_steps
    return result



if __name__ == "__main__":
    create_table()
    add_to_table(('python developer', "1,2,3,4,5,6"))