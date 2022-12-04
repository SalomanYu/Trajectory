from loguru import logger

import settings.tools as tools
import settings.config as config
from settings.config import EdwicaProfession, ResumeGroup, DefaultLevelProfession, ProfessionStatistic, LevelStatistic
from steps.step_4.tools import get_default_average_value


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
        while prof.levels[1].value - prof.levels[0].value < 5: prof.levels[0].value -= 1 # Искуственно снижаем опыт стажеров, если он больше джуновского на 5 месяцев
        while prof.levels[1].value - prof.levels[0].value < 3: prof.levels[1].value += 1 # Пока опыт джуна не превышает опыта стажера на 3 месяца, добавляем к опыту джуна месяц опыта
        while prof.levels[2].value - prof.levels[1].value < 12: prof.levels[2].value += 1 # Пока опыт миддла не превышает опыта джуна на 12 месяцев (год), добавляем к опыту миддла месяц опыта
        while prof.levels[3].value - prof.levels[2].value < 12: prof.levels[3].value += 1 # Пока опыт синьора не превышает опыта миддла на 12 месяцев (год), добавляем к опыту синьора месяц опыта    

    return data_for_correct # возращаем измененный список со статистикой 


def get_average_duration(resumes: list[ResumeGroup]) -> list[ProfessionStatistic[LevelStatistic]]:
    professions_statistic: list[ProfessionStatistic[LevelStatistic]] = []

    INTERN_STATISTICS = [0, 0] # Здесь хранится информация в месяцах, а вторую ячейку занимает количество профессий
    JUNIOR_STATISTICS = [0, 0] 
    MIDDLE_STATISTICS = [0, 0]  
    SENIOR_STATISTICS = [0, 0]  

    for item in resumes:
        resume = item.ITEMS[0]
        if (resume.groupId, resume.area) not in ((prof.prof_id, prof.area) for prof in professions_statistic): # Элементами в списке профессий будут являться професси с разными айди. Все профессии с совпадющими айди будут фигурироваться в одной статистике и отличаться лишь уровнем
            professions_statistic.append(ProfessionStatistic( # Заполняем шаблон дефолтными значениями для удобной работы
                prof_id=resume.groupId,
                area=resume.area,
                levels=(
                    LevelStatistic(name='intern', level=1, value=0),
                    LevelStatistic(name='junior', level=2, value=0),
                    LevelStatistic(name='middle', level=3, value=0),
                    LevelStatistic(name='senior', level=4, value=0))))

        if resume.level == 1: # Смотрим в какую статистику нужно занести опыт соискателя
            INTERN_STATISTICS[0] += tools.experience_to_months(resume.generalExcepience) # Добавляем полный стаж работы
            INTERN_STATISTICS[1] += 1 # Добавляем профессию, чтобы посчитать среднее арифметическое
            for step in item.ITEMS: # Сейчас будем проверять какого уровня должности занимал соискатель
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experiencePost.split()) and level_worlds.level == 1:
                        INTERN_STATISTICS[0] += tools.experience_to_months(step.experienceDuration) # Добавляем в статистику время занимаемой должности 
                        INTERN_STATISTICS[1] += 1
                        for item in professions_statistic: # Записываем в наш список статистики. Нулевой индекс значит, что мы выбираем стажеров
                            if item.prof_id == resume.groupId and item.area == resume.area: item.levels[0].value = get_default_average_value(INTERN_STATISTICS, level=1)

        elif resume.level == 2:
            JUNIOR_STATISTICS[0] += tools.experience_to_months(resume.generalExcepience)
            JUNIOR_STATISTICS[1] += 1
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experiencePost.split()) and level_worlds.level == 2:
                        JUNIOR_STATISTICS[0] += tools.experience_to_months(step.experienceDuration)
                        JUNIOR_STATISTICS[1] += 1
                        for item in professions_statistic:
                            if item.prof_id == resume.groupId and item.area == resume.area: item.levels[1].value = get_default_average_value(statistic=JUNIOR_STATISTICS, level=2)
        elif resume.level == 3:
            MIDDLE_STATISTICS[0] += tools.experience_to_months(resume.generalExcepience)
            MIDDLE_STATISTICS[1] += 1
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experiencePost.split()) and level_worlds.level == 3:
                        MIDDLE_STATISTICS[0] += tools.experience_to_months(step.experienceDuration)
                        MIDDLE_STATISTICS[1] += 1
                        for item in professions_statistic:
                            if item.prof_id == resume.groupId: item.levels[2].value = get_default_average_value(statistic=MIDDLE_STATISTICS, level=3)
        elif resume.level == 4:
            SENIOR_STATISTICS[0] += tools.experience_to_months(resume.generalExcepience)
            SENIOR_STATISTICS[1] += 1
            for step in item.ITEMS:
                for level_worlds in tools.LEVEL_KEYWORDS:
                    if level_worlds.key_words & set(step.experiencePost.split()) and level_worlds.level == 4:
                        SENIOR_STATISTICS[0] += tools.experience_to_months(step.experienceDuration)
                        SENIOR_STATISTICS[1] += 1
                        for item in professions_statistic:
                            if item.prof_id == resume.groupId: item.levels[3].value = get_default_average_value(statistic=SENIOR_STATISTICS, level=4)
    return professions_statistic


def rename_zero_professions_by_experience(resumes: list[ResumeGroup],
default_names:tuple[set[DefaultLevelProfession]], profession_default_values:list[ProfessionStatistic],
edwica_db_names:list[EdwicaProfession]) -> list[ResumeGroup]:
    
    for resume in resumes:
        previos_current_profession = True # проверяем был ли предыдущий этап в карьере правильным, то есть соответствующим искомой профессии
        job_steps = resume.ITEMS
        global_experience = tools.experience_to_months(job_steps[0].generalExcepience)
        for prof_statistic in profession_default_values:
            if (prof_statistic.prof_id == job_steps[0].groupId) and (prof_statistic.area == job_steps[0].area):
                for statistic_level in prof_statistic.levels:
                    if global_experience >= statistic_level.value:
                        # ВАЖНО! Бывает такое, что у некоторых групп с профессиями нет определенного уровня и чтобы у нас не
                        # вылетала ошибка из-за того, что опыт соответствует определенному уровню, которого нет в конкретной
                        # группе с профессиями, то мы вызываем исключение и присваем ему значения из ПЕРВОЙ группы с профессиями 
                        try:  
                            current_name = [i.name for i in default_names 
                                if i.level == statistic_level.level and i.profID == prof_statistic.prof_id 
                                and i.area == job_steps[0].area and prof_statistic.area == job_steps[0].area][0]  
                            logger.info(f"[id:{job_steps[0].db_id}/Ex:{global_experience}/group:{prof_statistic.prof_id}] Повысили профессию до {statistic_level.name.upper()} уровня {job_steps[0].title} -> {current_name}")
                        except IndexError:
                            try: 
                                current_name = [i.name for i in default_names 
                                    if i.level == statistic_level.level and i.area == job_steps[0].area and prof_statistic.area == job_steps[0].area][0]
                            except IndexError: exit(default_names)
                            logger.info(f"[id:{job_steps[0].db_id}/Ex:{global_experience}/group:{prof_statistic.prof_id}] Повысили профессию до {statistic_level.name.upper()} уровня {job_steps[0].title} -> {current_name}")

                        for step in job_steps: step.title = current_name
                        for step in job_steps: step.level = statistic_level.level
        
        for step_count, step in enumerate(job_steps[::-1]):
            step_has_changed = False
            level_step_is_zero = True
            for db_name in edwica_db_names:
                if (db_name.name.strip().lower() in step.experiencePost.strip().lower()) and (db_name.area == step.area) and (not step_has_changed):
                    previos_step = job_steps[step_count-1] # Ща будем проверять относится ли предыдуюший этап к 
                    if not db_name.name.strip().lower() in previos_step.experiencePost.strip().lower() and step_count != 0: # Проверяем, что это не самый первый этап карьеры, потому что это исключение, иначе мы возьмем минус первый элемент, который будет являться самым последним
                        previos_current_profession = False

                    for key_level in config.LEVEL_KEYWORDS:
                        if key_level.key_words & set(step.experiencePost.lower().split()):
                            level_step_is_zero = False
                            step.experiencePost = [i.name for i in default_names if i.level == key_level.level and i.area == step.area][0]

                    if level_step_is_zero:
                        if previos_current_profession:
                            post_experience = sum(list(map(tools.experience_to_months, [item.experienceDuration for item in job_steps[::-1][:step_count+1]])))
                        else:
                            post_experience = tools.experience_to_months(step.experiencePost)
                        
                        for prof_statistic in profession_default_values:
                            if (prof_statistic.prof_id == step.groupId) and (prof_statistic.area == step.area):
                                for statistic_level in prof_statistic.levels:
                                    if post_experience >= statistic_level.value:
                                        # Смотри описания исключения выше
                                        try:
                                            current_name = [i.name for i in default_names 
                                                if i.level == statistic_level.level and i.profID == prof_statistic.prof_id
                                                and prof_statistic.area == step.area and i.area == step.area][0]
                                            logger.info(f"[id:{job_steps[0].db_id}/Ex:{post_experience}/group:{prof_statistic.prof_id}] Повысили должность до {statistic_level.name.upper()} уровня {step.experiencePost} -> {current_name}")
                                        except IndexError: 
                                            current_name = [i.name for i in default_names 
                                                if i.level == statistic_level.level and prof_statistic.area == job_steps[0].area and i.area == job_steps[0].area][0]
                                            logger.info(f"[id:{job_steps[0].db_id}/Ex:{post_experience}/group:{prof_statistic.prof_id}] Повысили должность до {statistic_level.name.upper()} уровня {step.experiencePost} -> {current_name}")
                                        step.experiencePost = current_name
                                        step_has_changed = True
    return resumes
