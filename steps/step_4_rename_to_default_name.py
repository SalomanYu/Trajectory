"""
Данный код будет приводить все названия резюме и названия этапов к единому виду, соответствующих значению "Вес профессии в уровне"
"""

import logging
import xlrd 

import tools, config
from config import  DefaultLevelProfession


def get_default_names(profession_excelpath: str) -> tuple[set[DefaultLevelProfession], list]:
    book_reader = xlrd.open_workbook(profession_excelpath)
    work_sheet = book_reader.sheet_by_name("Вариации названий")
    table_titles = work_sheet.row_values(0)

    for col_num in range(len(table_titles)):
        match table_titles[col_num]:
            case "Наименование професии и различные написания":
                table_names_col = col_num
            case "Вес профессии в уровне":
                table_weight_in_level_col = col_num
            case "Уровень должности":
                table_level_col = col_num
            case "Вес профессии в соответсвии":
                table_weight_in_group = col_num
            case "ID список профессий":
                table_groupID_col = col_num
    
    names = [item for item in work_sheet.col_values(table_names_col) if item != '']
    default_names = set()

    for row_num in range(work_sheet.nrows):
        # Это условие фильтрует профессии по 'Id список профессий'
        # Если кортежа с содержимым (айди профессии, уровень профессии) нет в таком же кортеже дефолтных значений, то добавляем профессию
        if (work_sheet.cell(row_num, table_groupID_col), work_sheet.cell(row_num, table_level_col) not in 
            ((default.profID, default.level) for default in default_names)):

            if (work_sheet.cell(row_num, table_weight_in_level_col).value == 0) and (work_sheet.cell(row_num, table_weight_in_group).value == 1):
                default_names.add(DefaultLevelProfession(
                    profID=int(work_sheet.cell(row_num, table_groupID_col).value), 
                    name=work_sheet.cell(row_num, table_names_col).value, 
                    level=int(work_sheet.cell(row_num, table_level_col).value)))
            
            elif work_sheet.cell(row_num, table_weight_in_level_col).value == 1:
                default_names.add(DefaultLevelProfession(
                    profID=int(work_sheet.cell(row_num, table_groupID_col).value), 
                    name=work_sheet.cell(row_num, table_names_col).value, 
                    level=int(work_sheet.cell(row_num, table_level_col).value)))
        
    return default_names, names

def set_resume_names_to_default_values(log: logging):
    resumes = tools.load_resumes_json(log=log, path=config.STEP_3_JSON_FILE)
    level_default_names, edwica_db_names = get_default_names(profession_excelpath="Professions/43 Маркетинг _ Реклама. _ PR.xlsx")

    for resume in resumes:
        job_steps = resume.ITEMS
        resume_level = job_steps[0].level
        for default in level_default_names:
            default_level, default_name = default
            if resume_level == default_level:
                for db_name in edwica_db_names:
                    if db_name.strip().lower() in job_steps[0].name.strip().lower():
                        log.info("[ID: %d] Поменяли наименование РЕЗЮМЕ: %s -> %s", job_steps[0].db_id , job_steps[0].name, default_name)
                        for item in job_steps: item.name = default_name # меняем наименование профессии везде
                    
        for step in job_steps:
            name_step_has_changed = False
            step_doesnt_have_level = True
            for db_name in edwica_db_names:
                if db_name.strip().lower() == step.experience_post.strip().lower():
                    for key_level in config.LEVEL_KEYWORDS:
                        if key_level.key_words & set(step.experience_post.lower().split()):
                            for default_level, default_name in level_default_names:
                                if default_level == key_level.level:
                                    step_doesnt_have_level = False
                                    log.info("[%d]Поменяли ДОЛЖНОСТЬ: %s -> %s",step.db_id, step.experience_post, default_name)
                                    name_step_has_changed = True
                    # Если должность встречается в базе, но мы не смогли определить ее уровень, то присваеваем ей дефолное наименование нулевого уровня
                    if step_doesnt_have_level:
                        step.experience_post = [default.name for default in level_default_names if default.level == 0][0]
                        log.info("[%d]Поменяли НУЛЕВУЮ ДОЛЖНОСТЬ: %s -> %s",step.db_id, step.experience_post, [default.name for default in level_default_names if default.level == 0][0])
                        name_step_has_changed = True
            if not name_step_has_changed: # Если мы не смогли заменить должность на дефолтное наименование этой сферы, то попробуем найти такую дефолтное значение в других профессиях
                pass
                    
    
    tools.save_resumes_to_json(log=log, resumes=resumes, filename=config.STEP_4_JSON_FILE)


if __name__ == "__main__":
    log = tools.start_logging("step_4.log")
    set_resume_names_to_default_values(log)         
