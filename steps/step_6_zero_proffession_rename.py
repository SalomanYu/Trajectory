import logging
import tools, config
from config import ResumeGroup, DefaultLevelProfession



def get_average_duration(resumes: list[ResumeGroup]):
    INTERN_STATISTICS = set()
    JUNIOR_STATISTICS = set()
    MIDDLE_STATISTICS = set()
    SENIOR_STATISTICS = set()

    for item in resumes:        
        resume = item.ITEMS[0]
        if resume.level == 1:
            INTERN_STATISTICS.add(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 1:
                        INTERN_STATISTICS.add(tools.experience_to_months(step.experience_duration))
        elif resume.level == 2:
            JUNIOR_STATISTICS.add(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 2:
                        JUNIOR_STATISTICS.add(tools.experience_to_months(step.experience_duration))
        elif resume.level == 3:
            MIDDLE_STATISTICS.add(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 3:
                        MIDDLE_STATISTICS.add(tools.experience_to_months(step.experience_duration))
        elif resume.level == 4:
            SENIOR_STATISTICS.add(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 4:
                        SENIOR_STATISTICS.add(tools.experience_to_months(step.experience_duration))

    
    print(f"{INTERN_STATISTICS=}\t{JUNIOR_STATISTICS=}\t{MIDDLE_STATISTICS=}\t{SENIOR_STATISTICS=}")
    average_intern = tools.get_default_average_value(statistic=INTERN_STATISTICS, level=1)
    average_junior = tools.get_default_average_value(statistic=JUNIOR_STATISTICS, level=2)
    average_middle = tools.get_default_average_value(statistic=MIDDLE_STATISTICS, level=3)
    average_senior = tools.get_default_average_value(statistic=SENIOR_STATISTICS, level=4)

    return average_intern,  average_junior, average_middle, average_senior

def rename_zero_professions_by_experience(log:logging, resumes: list[ResumeGroup], default_names:set[DefaultLevelProfession], edwica_db_names:list):
    # log = tools.start_logging("step_test.log")
    # resumes = tools.load_resumes_json(log=log, path=tools.STEP_5_JSON_FILE)

    # default_names, edwica_db_names = get_default_names(profession_excelpath="Professions/43 Маркетинг _ Реклама. _ PR.xlsx")

    for resume in resumes:
        previos_current_profession = True # проверяем был ли предыдущий этап в карьере правильным, то есть соответствующим искомой профессии
        job_steps = resume.ITEMS
        if job_steps[0].level == 0:
            global_experience = tools.experience_to_months(job_steps[0].general_experience)
            for level_values in config.DEFAULT_LEVEL_EXPERIENCE:
                if level_values.min_value <= global_experience <= level_values.max_value:
                    new_resume_name = [i.name for i in default_names if i.level == level_values.level][0]
                    for step in job_steps: step.name = new_resume_name
        
        for step_count, step in enumerate(job_steps[::-1]):
            level_step_is_zero = True
            for db_name in edwica_db_names:
                if db_name.strip().lower() in step.experience_post.strip().lower():
                    previos_step = job_steps[step_count-1] # Ща будем проверять относится ли предыдуюший этап к 
                    if not db_name.strip().lower() in previos_step.experience_post.strip().lower() and step_count != 0: # Проверяем, что это не самый первый этап карьеры, потому что это исключение, иначе мы возьмем минус первый элемент, который будет являться самым последним
                        previos_current_profession = False

                    for key_level in config.LEVEL_KEYWORDS:
                        if key_level.key_words & set(step.experience_post.lower().split()):
                            level_step_is_zero = False
                            step.experience_post = [i.name for i in default_names if i.level == key_level.level][0]

                    if level_step_is_zero:
                        if previos_current_profession:
                            post_experience = sum(list(map(tools.experience_to_months, [item.experience_duration for item in job_steps[::-1][:step_count+1]])))
                        else:
                            post_experience = tools.experience_to_months(step.experience_post)
                        
                        for level_values in tools.DEFAULT_LEVEL_EXPERIENCE:
                            if  level_values.min_value <= post_experience <= level_values.max_value:
                                # if level_values.level == 1: print(resume.ID)
                                log.info("%s -->  %s", step.experience_post, {[i.name for i in default_names if i.level == level_values.level][0]})
                                step.experience_post = [i.name for i in default_names if i.level == level_values.level][0]
                                
    tools.save_resumes_to_json(log, resumes, filename=tools.STEP_6_JSON_FILE)   


    