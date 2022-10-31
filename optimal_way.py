from typing import NamedTuple
from operator import attrgetter
from rich.progress import track

from settings.config import *
from settings.tools import group_steps_to_resume, experience_to_months
import settings.database as database

####### Поиск оптимального пути среди профессий

class SuitableWay(NamedTuple): # Подходящий путь
    resumeId: int
    duration: int # Время достижения пути в месяцах
    stepsCount: int

class OneStepWay(NamedTuple):
    id: int
    title:str
    post: str
    generalExperience: str
    duration: str
    resumeId: str


def find_optimal_ways_for_this_professions(tablename: str, profession_name: str, count: int = 3, sort_type:int =1):
    """Метод получает на вход название профессии и ищет по БД все совпадения с названием профессии в наименовании резюме и этапах"""
    found_options : list[SuitableWay] = [] 
    data = database.get_all_resumes(tablename)
    grouped_steps = group_steps_to_resume(data)

    for resume in grouped_steps:
        subtableWay = __find_SubtableWay(resume, profession_name)
        if subtableWay: found_options += subtableWay
    
    return __show_most_optimal_ways(resumes=grouped_steps, count=count, found_options=found_options, sort_type=sort_type)
    

def __find_SubtableWay(resume:ResumeGroup, profession_name:str) -> list[SuitableWay] | None:
    """Метод, который определяет совпадает название искомой профессии с названием резюме или этапа
    Если профессия совпадает с названием резюме, то мы переводим общий стаж работы в количество месяцев и записываем в options
    Если профессия совпадает с названием этапа, то мы переводим весь стаж до этого этапа в количество месяцев и записываем в options
    Еще я учитываю, что название профессии может встречаться и в названии резюме и в шаге. Если так, то сохраняем оба значения в options
    Так мы сможем составить более точную статистику"""
    options : list[SuitableWay] = [] # т.к вариантов в одном резюме может быть несколько
    unique_similar_ids : set[int] = set() # если similarId есть в этом множестве, значит этот путь мы уже рассматривали
    if profession_name is None:
        ...
    
    for index, step in enumerate(resume.ITEMS):
        if step.experiencePost.lower() == profession_name.lower().strip() and step.similarPathId not in unique_similar_ids:
            unique_similar_ids.add(step.similarPathId)
            required_experience = sum((experience_to_months(step.experienceDuration) for step in resume.ITEMS[:index]))
            if required_experience == 0: required_experience = experience_to_months(step.experienceDuration) # Это делается потому, что первый этап отличается от второго этапа и названия резюме
            options.append(SuitableWay(resumeId=step.db_id, duration=required_experience, stepsCount=index+1))
    
    if step.title.lower() == profession_name.lower().strip():
        unique_similar_ids.add(step.similarPathId)
        required_experience = experience_to_months(step.generalExcepience)
        options.append(SuitableWay(resumeId=step.db_id, duration=required_experience, stepsCount=len(resume.ITEMS)))
    return options

def __show_most_optimal_ways(count:int, found_options:list[SuitableWay], 
    resumes: list[ResumeGroup], sort_type: int) -> list[ResumeGroup]:
    """Сортируем найденные пути по продолжительности в порядке возрастания и по айди шага ищем резюме в нашей БД уникальных путей"""
    options : list[list[ProfessionStep, SuitableWay]] = []
    if sort_type == 1: work_list = sorted(found_options, key=attrgetter("duration"), reverse=reverse)
    else: work_list = sorted(found_options, key=attrgetter("stepsCount"),  reverse=reverse)
    
    for way in work_list:
        if count == 0: break
        count -= 1
        current_db_id = way.resumeId
        options.append([resume.ITEMS[:way.stepsCount] for resume in resumes for step in resume.ITEMS 
                        if step.db_id== current_db_id] + [way])
    return options


if __name__ == "__main__":
    # profession = input("Введите название професси: ")
    # count = int(input("Количество путей: "))
    # sort_type = int(input("Сортировать по:\n    1.Количеству шагов (По умолчанию)\n    2.Продолжительности\n>>> "))
    # reverse = int(input('Сортировать по:\n     1.По возрастанию\n     2.По убыванию\n>>> '))
    # if reverse == 1: reverse = False
    # else: reverse = True
    reverse= False

    options = find_optimal_ways_for_this_professions(tablename='Ветеринария', profession_name='')
    for way in options:
        result = "->".join([f"{step.experiencePost}" for step in way[0] if step.experiencePost])
        if not result: result = way[0][0].title
        print(result + f" ({way[1].duration} мес./{way[1].stepsCount} шаг.)")