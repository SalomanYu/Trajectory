"""
"""

import logging
import tools, config
from config import ResumeGroup


def filtering_groups(log:logging, data: list[ResumeGroup]) -> tuple[list[ResumeGroup], list[ResumeGroup.ID]]:
    """
        This method будет искать индентичные группы. Путем сравнения двух резюме, мы будем узнавать уровень схожести двух резюме
    В основе лежит цикл - один ко многим, в котором мы пытаемся набрать необходимое количество очков для того,
    чтобы понять насколько резюме похожи.
    Когда мы наберем максимальное количество очков(4),  мы можем сделать вывод, что резюме одинаковые. Следовательно, одно из них
    мы добавим в список дубликатов.
    
        В качестве аутпута выдаем кортеж - измененный массив данных в формате кортеж с кортежами  и так же выдаем список дубликатов
    для последуюшего удаления
    """

    dublicate_list = [] # Инициализация переменной, которая будет хранить дубликаты

    log.info("Start cicle finding duplicates")
    for current_index in range(len(data)):
        # В основе сравнения лежит метод - один ко многим. То есть берем по порядку группу и сраниваем ее со всеми остальными
        currentResume = data[current_index].ITEMS[0] # Выделяем первый этап карьеры, чтобы удобнее было работать с общими для всех этапов данными (стаж, наименование резюме, ЗП, скиллы и тд)
        currentJobStepsCount = len(data[current_index].ITEMS)
        currentSteps = data[current_index].ITEMS        
        
        for comporable_index in range(current_index+1, len(data)):
            # Переменная отвечающая за степень схожести групп
            similar_count = 0

            comporableResume = data[comporable_index].ITEMS[0] # Выделяем первый этап карьеры, чтобы удобнее было работать с общими для всех этапов данными (стаж, наименование резюме, ЗП, скиллы и тд)
            comporableJobStepsCount = len(data[comporable_index].ITEMS)
            comporableSteps = data[comporable_index].ITEMS
            
            if currentResume.name == comporableResume.name:
                similar_count += 1
            if currentResume.general_experience == comporableResume.general_experience:
                similar_count += 1
            if currentJobStepsCount == comporableJobStepsCount:
                similar_count += 1
                steps_similart_count = 0 # Считает количество совпадений в этапах

                for step in range(currentJobStepsCount):                    
                    if (currentSteps[step].experience_post == comporableSteps[step].experience_post) and \
                       (currentSteps[step].experience_duration == comporableSteps[step].experience_duration) and \
                       (currentSteps[step].experience_interval == comporableSteps[step].experience_interval):
                            steps_similart_count += 1
                if steps_similart_count == currentJobStepsCount:
                    similar_count += 1

            # Что мы делаем, когда находим дубликаты
            if similar_count == 4 or (similar_count == 3 and currentResume.name != comporableResume.name):
                log.warning("Duplicate finded! Look these links: \n1. %s \n2. %s", data[current_index].ID, data[comporable_index].ID)
                # Так как одно из похожих резюме будет удалено, то попытаемся забрать у него некоторую информацию при условии, что она у него есть (типо берем  более свежую инфу)
                for step in comporableSteps:
                    if (currentResume.salary != step.salary) and (step.salary == ""):
                        step.salary = currentResume.salary
                    if (currentResume.languages != step.languages) and (step.languages == ""):
                        step.languages = currentResume.languages
                    if (currentResume.skills != step.skills) and (step.skills == ""):
                        step.skills = currentResume.skills
                    if (currentResume.university_name != step.university_name) and (step.university_name == ''):
                        step.university_name = currentResume.university_name
                    if (currentResume.university_direction != step.university_direction) and (step.university_direction == ''):
                        step.university_direction = currentResume.university_direction
                    if (currentResume.university_year != step.university_year) and (step.university_year == ''):
                        step.university_year = currentResume.university_year
                dublicate_list.append(data[current_index].ID)

    return data, dublicate_list



def remove_dublicates(log:logging, data:list[ResumeGroup], list_to_delete: list) -> dict:
    if list_to_delete:
        log.warning("Finded %d duplicates", len(list_to_delete))
        for candidat in data:
            if candidat.ID in list_to_delete: 
                data.remove(candidat)
                log.warning("Removed duplicate - %s", candidat.ITEMS[0].name)
    else:
        log.warning("Duplicate list is empty")
    return data


if __name__ == "__main__":
    log = tools.start_logging(logfile="step_3.log")

    # data = settings.load_resumes_json(log, settings.STEP_2_JSON_FILE)
    resumes = tools.load_resumes_json(log=log, filename=config.STEP_2_JSON_FILE)
    data, dublicate_list = filtering_groups(resumes)
    # retransled_dict = settings.nested_tuple_to_dict(nested_tuple=groups)

    data_without_dublicates = remove_dublicates(data=data, list_to_delete=dublicate_list)
    tools.save_to_json(log, data_without_dublicates, settings.STEP_3_JSON_FILE)
