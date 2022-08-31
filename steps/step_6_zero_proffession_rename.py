import logging
from pprint import pprint
import tools, config
from config import ResumeGroup, DefaultLevelProfession, ProfessionStatistic, LevelStatistic

def corrent_min_interval_between_levels(data: list[ProfessionStatistic]) -> list[ProfessionStatistic]:
    """
    Метод будет выявлять неккоректную статистику и корректировать ее. А как мы будем понимать, что со статистикой что-то не так? \n
    - Средний стаж более низкого уровня должности равен или превышает старший по отношению к нему уровень должности. 
    То есть, если у уровня 1, средний стаж равен 2 годам, а у уровня 3 - 1 году\n
    - Если промежуток между уровнями не соответствует минимальному значению\n\n
    Минимальные значения между уровнями:\n
    
    - Стажер -> Джун:минимум: 3 месяца\n
    - Джун -> Миддл:минимум: 12 месяцев\n
    - Миддл -> Сеньор:минимум: 12 месяцев\n

    """
    data_for_correct = data[::] # копируем содержимое исходного списка, чтобы сохранить оба варианта
    for prof in data_for_correct:
        # print(prof.levels)
        while prof.levels[1].value - prof.levels[0].value < 5: prof.levels[0].value -= 1 # Искуственно снижаем опыт стажеров, если он больше джуновского на 5 месяцев
        while prof.levels[1].value - prof.levels[0].value < 3: prof.levels[1].value += 1 # Пока опыт джуна не превышает опыта стажера на 3 месяца, добавляем к опыту джуна месяц опыта
        while prof.levels[2].value - prof.levels[1].value < 12: prof.levels[2].value += 1 # Пока опыт миддла не превышает опыта джуна на 12 месяцев (год), добавляем к опыту миддла месяц опыта
        while prof.levels[3].value - prof.levels[2].value < 12: prof.levels[3].value += 1 # Пока опыт синьора не превышает опыта миддла на 12 месяцев (год), добавляем к опыту синьора месяц опыта    

        # print(prof.levels, "\n-------------------------\n")
    return data_for_correct # возращаем измененный список со статистикой 

    
             

def get_average_duration(resumes: list[ResumeGroup]) -> list[ProfessionStatistic]:
    professions_statistic = []

    INTERN_STATISTICS = []
    JUNIOR_STATISTICS = []
    MIDDLE_STATISTICS = []
    SENIOR_STATISTICS = []

    for item in resumes:
        resume = item.ITEMS[0]
        if resume.groupID not in (prof.prof_id for prof in professions_statistic): # Элементами в списке профессий будут являться професси с разными айди. Все профессии с совпадющими айди будут фигурироваться в одной статистике и отличаться лишь уровнем
            professions_statistic.append(ProfessionStatistic( # Заполняем шаблон дефолтными значениями для удобной работы
                prof_id=resume.groupID,
                levels=(
                    LevelStatistic(name='intern', level=1, value=0),
                    LevelStatistic(name='junior', level=2, value=0),
                    LevelStatistic(name='middle', level=3, value=0),
                    LevelStatistic(name='senior', level=4, value=0))))

        if resume.level == 1: # Смотрим в какую статистику нужно занести опыт соискателя
            INTERN_STATISTICS.append(tools.experience_to_months(resume.general_experience)) # Добавляем полный стаж работы
            for step in item.ITEMS: # Сейчас будем проверять какого уровня должности занимал соискатель
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 1:
                        INTERN_STATISTICS.append(tools.experience_to_months(step.experience_duration)) # Добавляем в статистику время занимаемой должности 
                        for item in professions_statistic: # Записываем в наш список статистики. Нулевой индекс значит, что мы выбираем стажеров
                            if item.prof_id == resume.groupID: item.levels[0].value = tools.get_default_average_value(statistic=INTERN_STATISTICS, level=1)

        elif resume.level == 2:
            JUNIOR_STATISTICS.append(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 2:
                        JUNIOR_STATISTICS.append(tools.experience_to_months(step.experience_duration))
                        for item in professions_statistic:
                            if item.prof_id == resume.groupID: item.levels[1].value = tools.get_default_average_value(statistic=JUNIOR_STATISTICS, level=2)
        elif resume.level == 3:
            MIDDLE_STATISTICS.append(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 3:
                        MIDDLE_STATISTICS.append(tools.experience_to_months(step.experience_duration))
                        for item in professions_statistic:
                            if item.prof_id == resume.groupID: item.levels[2].value = tools.get_default_average_value(statistic=MIDDLE_STATISTICS, level=3)
        elif resume.level == 4:
            SENIOR_STATISTICS.append(tools.experience_to_months(resume.general_experience))
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experience_post.split()) and level_worlds.level == 4:
                        SENIOR_STATISTICS.append(tools.experience_to_months(step.experience_duration))
                        for item in professions_statistic:
                            if item.prof_id == resume.groupID: item.levels[3].value = tools.get_default_average_value(statistic=SENIOR_STATISTICS, level=4)
    return past_default_values(professions_statistic)

def past_default_values(professions_statistic: list[ProfessionStatistic]) -> list[ProfessionStatistic]:
    """Метод используется для того, чтобы заменить пустые значения среднего уровня дефолтными"""
    for profession in professions_statistic:
        statistic = profession.levels
        for item in statistic:
            if not item.value:
                for default in config.DEFAULT_LEVEL_EXPERIENCE:
                    if default.level == item.level: item.value = default.min_value
    return professions_statistic


def rename_zero_professions_by_experience(log:logging, resumes: list[ResumeGroup],
 default_names:set[DefaultLevelProfession], profession_default_values:list[ProfessionStatistic], edwica_db_names:list) -> None:
    for resume in resumes:
        
        previos_current_profession = True # проверяем был ли предыдущий этап в карьере правильным, то есть соответствующим искомой профессии
        job_steps = resume.ITEMS
        # if job_steps[0].level == 0:
        global_experience = tools.experience_to_months(job_steps[0].general_experience)
        for prof_statistic in profession_default_values:
            if prof_statistic.prof_id == job_steps[0].groupID:
                for statistic_level in prof_statistic.levels:
                    if global_experience >= statistic_level.value:
                        try:  # ВАЖНО
                            # Бывает такое, что у некоторых групп с профессиями нет определенного уровня и чтобы у нас не вылетала ошибка из-за того, что опыт соответствует определенному уровню
                            # которого нет в конкретной группе с профессиями, то мы вызываем исключение и присваем ему значения из ПЕРВОЙ группы с профессиями 
                            current_name = [i.name for i in default_names if i.level == statistic_level.level and i.profID == prof_statistic.prof_id][0] 
                            log.info("[id:%d/Ex:%d/group:%d] Повысили нулевую профессию до %s уровня %s -> %s", job_steps[0].db_id,global_experience,prof_statistic.prof_id, statistic_level.name.upper(), job_steps[0].name, current_name)
                        
                        except IndexError: 
                            current_name = [i.name for i in default_names if i.level == statistic_level.level][0]
                            log.info("[BR-id:%d/Ex:%d/group:%d] Повысили нулевую профессию до %s уровня %s -> %s", job_steps[0].db_id,global_experience,prof_statistic.prof_id, statistic_level.name.upper(), job_steps[0].name, current_name)

                        for step in job_steps: step.name = current_name
                        for step in job_steps: step.level = statistic_level.level
        
        for step_count, step in enumerate(job_steps[::-1]):
            step_has_changed = False
            level_step_is_zero = True
            for db_name in edwica_db_names:
                if db_name.strip().lower() in step.experience_post.strip().lower() and not step_has_changed:
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
                        
                        for prof_statistic in profession_default_values:
                            if prof_statistic.prof_id == step.groupID:
                                for statistic_level in prof_statistic.levels:
                                    if post_experience >= statistic_level.value:
                                        try:
                                            current_name = [i.name for i in default_names if i.level == statistic_level.level and i.profID == prof_statistic.prof_id][0]
                                            log.info("[id:%d/Ex:%d/group:%d] Повысили нулевую должность  до %s уровня %s -> %s",step.db_id, post_experience, prof_statistic.prof_id, statistic_level.name.upper(), step.experience_post, current_name)
                                        except IndexError: 
                                            current_name = [i.name for i in default_names if i.level == statistic_level.level][0]
                                            log.info("[BR-id:%d/Ex:%d/group:%d] Повысили нулевую должность  до %s уровня %s -> %s",step.db_id, post_experience, prof_statistic.prof_id, statistic_level.name.upper(), step.experience_post, current_name)
                                        step.experience_post = current_name
                                        step_has_changed = True
    tools.save_resumes_to_json(log, resumes, filename=tools.JSONFILE.STEP_6.value)   

if __name__ == "__main__":
    corrent_min_interval_between_levels(data='')