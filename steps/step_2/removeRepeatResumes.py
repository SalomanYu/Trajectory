from loguru import logger
from settings.config import ResumeGroup, ProfessionStep
from rich.progress import track

from typing import NamedTuple

class ComparisonStepInfo(NamedTuple):
    Post        :str
    Duration    :str
    Interval    :str


class ComparisonResumeInfo(NamedTuple):
    Title               :str
    StepsCount          :str
    GeneralExperience   :str
    Steps               :tuple[ComparisonStepInfo]

    

def filtering_groups(data: list[ResumeGroup]) -> tuple[list[ResumeGroup], list[ResumeGroup.ID]]:
    """
    Этот метод будет искать одинаковые резюме. Когда мы будем сравнивать два резюме, 
    мы будем видеть степень схожести двух резюме
    В основе лежит цикл - один ко многим, в котором мы пытаемся набрать необходимое количество очков для того,
    чтобы понять насколько два резюме повторяют друг друга.
    Когда мы наберем максимальное количество очков(4), мы можем сделать вывод, что резюме одинаковые. 
    Следовательно, одно из них мы добавим в список дубликатов и удалим.
    
    Вывод:измененный массив данных в формате кортеж с кортежами  и так же выдаем список дубликатов
    для последуюшего удаления
    """
    dublicate_list: list[str] = [] # Инициализация переменной, которая будет хранить дубликаты
    logger.info("Ищем одинаковые резюме...")
    for current_index in track(range(len(data)), description='[blue]Фильтруем резюме'):
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
            
            if currentResume.title == comporableResume.title:
                similar_count += 1
            if currentResume.generalExcepience == comporableResume.generalExcepience:
                similar_count += 1
            if currentJobStepsCount == comporableJobStepsCount:
                similar_count += 1

                steps_similart_count = 0 # Считает количество совпадений в этапах
                for step in range(currentJobStepsCount):                    
                    if (currentSteps[step].experiencePost == comporableSteps[step].experiencePost) and \
                       (currentSteps[step].experienceDuration == comporableSteps[step].experienceDuration) and \
                       (currentSteps[step].experienceInterval == comporableSteps[step].experienceInterval):
                            steps_similart_count += 1
                if steps_similart_count == currentJobStepsCount:
                    similar_count += 1

            # Что мы делаем, когда находим дубликаты
            if similar_count == 4 or (similar_count == 3 and currentResume.title != comporableResume.title):
                # Так как одно из похожих резюме будет удалено, то попытаемся забрать у него некоторую информацию при условии, что она у него есть (типо берем  более свежую инфу)
                for step in comporableSteps:
                    if (currentResume.salary != step.salary) and (step.salary == ""):
                        step.salary = currentResume.salary
                    if (currentResume.languages != step.languages) and (step.languages == ""):
                        step.languages = currentResume.languages
                    if (currentResume.skills != step.skills) and (step.skills == ""):
                        step.skills = currentResume.skills
                    if (currentResume.educationUniversity != step.educationUniversity) and (step.educationUniversity == ''):
                        step.educationUniversity = currentResume.educationUniversity
                    if (currentResume.educationDirection != step.educationDirection) and (step.educationDirection == ''):
                        step.educationDirection = currentResume.educationDirection
                    if (currentResume.educationYear != step.educationYear) and (step.educationYear == ''):
                        step.educationYear = currentResume.educationYear
                dublicate_list.append(data[current_index].ID)
    return data, dublicate_list

def get_duplicates(resumes: list[ResumeGroup]) -> tuple[list[ResumeGroup], list[str]]:
    duplicates: list[str] = []
    for index1 in track(range(len(resumes)), description="[green]Фильтруем..."):
        resume1 = get_resume_info_for_comparison(resumes[index1])
        for index2 in range(index1+1, len(resumes)):
            resume2 = get_resume_info_for_comparison(resumes[index2])
            similarity = check_similarity_between_two_resumes(resume1, resume2)
            if similarity:
                resume2 = merge_two_resumes(resumes[index1], resumes[index2])
                duplicates.append(resumes[index1].ID)
    print(f"Duplicates count: {len(duplicates)}")
    return (resumes, duplicates)
            
def get_resume_info_for_comparison(resume: ResumeGroup) -> ComparisonResumeInfo:
    steps = get_steps_info_for_comparison(resume.ITEMS)
    return ComparisonResumeInfo(
        Title=resume.ITEMS[0].title,
        StepsCount=len(resume.ITEMS),
        GeneralExperience=resume.ITEMS[0].generalExcepience,
        Steps=steps
    )

def get_steps_info_for_comparison(steps: list[ProfessionStep]) -> list[ComparisonStepInfo]:
    steps_ = []
    for step in steps:
        steps_.append(ComparisonStepInfo(
            Post=step.experiencePost,
            Duration=step.experienceDuration,
            Interval=step.experienceInterval
        ))
    return steps_


def check_similarity_between_two_resumes(resume1: ComparisonResumeInfo, resume2: ComparisonResumeInfo) -> bool:
    similarityCount = 0
    if resume1.Title == resume2.Title: similarityCount += 1
    if resume1.Steps == resume2.Steps: similarityCount += 1
    if resume1.StepsCount == resume2.StepsCount: similarityCount += 1 
    if resume1.GeneralExperience == resume2.GeneralExperience: similarityCount += 1

    if similarityCount == 4 or (similarityCount == 3 and resume1.Title != resume2.Title):
        return True
    return False

def merge_two_resumes(resume1: ResumeGroup, resume2: ResumeGroup) -> ResumeGroup:
    resume1Step = resume1.ITEMS[0]
    for step in resume2.ITEMS:
        if resume1Step.salary != step.salary and step.salary == "":
            step.salary = resume1Step.salary
        if resume1Step.languages != step.languages and step.languages == "":
            step.languages = resume1Step.languages
        if resume1Step.skills != step.skills and step.skills == "":
            step.skills = resume1Step.skills
        if resume1Step.educationUniversity != step.educationUniversity and step.educationUniversity == "":
            step.educationUniversity = resume1Step.educationUniversity
        if resume1Step.educationDirection != step.educationDirection and step.educationDirection == "":
            step.educationDirection = resume1Step.educationDirection
        if resume1Step.educationYear != step.educationYear and step.educationYear == "":
            step.educationYear = resume1Step.educationYear
    return resume2




def remove_dublicates(data:list[ResumeGroup], list_to_delete: list) -> list[ResumeGroup]:
    if list_to_delete:
        logger.warning(f"Найдено {len(list_to_delete)} одинаковых резюме")
        for candidat in data:
            if candidat.ID in list_to_delete: 
                data.remove(candidat)
                logger.warning(f"Удалили резюме - {candidat.ITEMS[0].title}")
    else:
        logger.warning("Мы не нашли ни одного дубликата среди резюме!")
    return data
