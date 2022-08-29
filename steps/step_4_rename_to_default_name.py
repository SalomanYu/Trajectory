"""
Данный код будет приводить все названия резюме и названия этапов к единому виду, соответствующих значению "Вес профессии в уровне"
"""

import logging
from fuzzywuzzy import fuzz
from rich.progress import track

import tools, config


def set_resume_names_to_default_values(log: logging, path: str):
    resumes = tools.load_resumes_json(log=log, path=config.STEP_3_JSON_FILE)
    level_default_names, edwica_db_names = tools.get_default_names(profession_excelpath=path)
    for item in track(range(len(resumes)), description="[blue]Приведение наименований должностей и профессии к стандартным значениям"):
        resume = resumes[item]
        job_steps = resume.ITEMS
        name_resume_has_changed= False
        resume_level = job_steps[0].level
        resume_groupID = job_steps[0].groupID
        for default in level_default_names:
            if name_resume_has_changed: break
            if resume_level == default.level and default.profID == resume_groupID:
                name_resume_has_changed = True
                log.info("[ID: %d] Поменяли наименование РЕЗЮМЕ: %s -> %s", job_steps[0].db_id , job_steps[0].name, default.name)
                for item in job_steps: item.name = default.name # меняем наименование профессии везде

        for step in job_steps:
            name_step_has_changed = False
            step_doesnt_have_level = True
            for db_name in edwica_db_names:
                if name_step_has_changed: break
                if db_name.strip().lower() == step.experience_post.strip().lower():
                    for key_level in config.LEVEL_KEYWORDS:
                        if key_level.key_words & set(step.experience_post.lower().split()):
                            for defID, default_level, default_name in level_default_names:
                                if default_level == key_level.level and not name_step_has_changed and defID == step.groupID:
                                    step_doesnt_have_level = False
                                    log.info("[%d]Поменяли ДОЛЖНОСТЬ[%d - %d]: %s -> %s",step.db_id, step.groupID, defID, step.experience_post, default_name)
                                    name_step_has_changed = True
                    # Если должность встречается в базе, но мы не смогли определить ее уровень, то присваеваем ей дефолное наименование нулевого уровня
                    if step_doesnt_have_level and not name_step_has_changed:
                        for default in level_default_names:
                            if fuzz.WRatio(s1=default.name, s2=step.experience_post) >= 90 and default.level == 0:
                                log.info("[%d]Поменяли НУЛЕВУЮ ДОЛЖНОСТЬ[%d - %d]: %s -> %s", step.db_id, step.groupID, default.profID, step.experience_post, default.name)
                                step.experience_post = default.name
                                name_step_has_changed = True
                if not name_step_has_changed:
                    current_name = tools.find_profession_in_proffessions_db(step.experience_post)
                    if current_name:
                        name_step_has_changed = True
                        log.info("[ID: %d] Нашли наименование ДОЛЖНОСТИ в других файлах: %s -> %s", step.db_id, step.experience_post, current_name)
                        for item in job_steps: item.name = current_name # меняем наименование профессии везде
                    else: log.info("[ID: %d] НЕ НАШЛИ наименование ДОЛЖНОСТИ в других файлах: %s", step.db_id, step.experience_post)
                   
            if not name_step_has_changed: # Если мы не смогли заменить должность на дефолтное наименование этой сферы, то попробуем найти такую дефолтное значение в других профессиях
                pass
                    
    
    tools.save_resumes_to_json(log=log, resumes=resumes, filename=config.STEP_4_JSON_FILE)


if __name__ == "__main__":
    log = tools.start_logging("step_4.log")
    set_resume_names_to_default_values(log)         
