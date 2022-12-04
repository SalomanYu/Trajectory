"""Здесь мы объединяем одинаковые этапы в карьере соискателя. Одинаковыми этапы считаются, если у них совпадают должности и отрасли на 100%"""

from rich.progress import track
from loguru import logger
import re

from settings.config import ResumeGroup, ProfessionStep


def merge_all_resumes_steps(resumes: list[ResumeGroup]) -> tuple[list[ResumeGroup], list[int]]:
    duplicates: list[int] = []
    
    for i in track(range(len(resumes)), description="[red]Объединение одинаковых этапов"):
        steps = resumes[i].ITEMS
        for item in range(1, len(steps)):
            if _check_similarity_between_two_steps(steps[item], steps[item-1]):
                steps[item] = _merge_two_steps(steps[item], steps[item-1])
                duplicates.append(steps[item-1].db_id)
    return (resumes, duplicates)

def _check_similarity_between_two_steps(step1: ProfessionStep, step2: ProfessionStep) -> bool:
    if step1.experiencePost.lower() == step2.experiencePost.lower():
        if step1.branch.lower() == step2.branch.lower() or (step1.branch == "" or step2.branch == ""):
            return True
    return False

def _merge_two_steps(step1: ProfessionStep, step2: ProfessionStep) -> ProfessionStep:
    START_WORK_PERIOD = 0
    END_WORK_PERIOD = -1
    mergedDuration = _mergeDurations(step1, step2)
    mergedInterval = ' — '.join((
        step1.experienceInterval.split('—')[START_WORK_PERIOD],
        step2.experienceInterval.split('—')[END_WORK_PERIOD]))
    step1.experienceInterval = mergedInterval
    step1.experienceDuration = mergedDuration
    return step1
    
def _mergeDurations(step1: ProfessionStep, step2: ProfessionStep) -> str:
    # Обрезаем лишние пробелы у строк (Метод strip() не помог)
    duration_first = ' '.join(step1.experienceDuration.split())
    duration_second = ' '.join(step1.experienceDuration.split())

    month_pattern = '\d{2} м|\d{2} m|\d м|\d m'
    year_pattern = '\d{2} г|\d{2} y|\d г|\d y|\d{2} л'
    try:months_first = int(re.findall(month_pattern, duration_first)[0].split(' ')[0])
    except IndexError:months_first = 0
    try:months_second = int(re.findall(month_pattern, duration_second)[0].split(' ')[0])
    except IndexError:months_second = 0
    try:years_first = int(re.findall(year_pattern, duration_first)[0].split(' ')[0])
    except IndexError:years_first = 0
    try:years_second = int(re.findall(year_pattern, duration_second)[0].split(' ')[0])
    except IndexError:years_second = 0

    # Делим на 12, потому что у нас 12 система счисления
    total_months = (months_first + months_second) % 12
    # Делим на 12, потому что у нас 12 система счисления
    total_years = years_first + years_second + \
        ((months_first + months_second) // 12)

    final_date = _get_current_date(years=str(total_years), months=str(total_months))
    return final_date

def _get_current_date(years: str, months: str) -> str:
    if months == '1': month_type = 'месяц'
    elif months in ('2', '3', '4'): month_type = 'месяца'
    else: month_type = 'месяцев'

    if years != '11' and str(years)[-1] == '1': year_type = 'год'
    elif years not in ('12', '13', '14') and str(years)[-1] in ('2', '3', '4'): year_type = 'года'
    else: year_type = 'лет'

    if years == '0': return ' '.join((months, month_type))
    elif months == '0': return ' '.join((years, year_type))

    return ' '.join((years, year_type, months, month_type))

def remove_repeat_steps(data:list[ResumeGroup], set_to_remove:set) -> list[ResumeGroup]:
    if set_to_remove:
        logger.warning(f"Было обнаружено {len(set_to_remove)} повторяющихся этапов. Они будут объединены и удалены")
        print(f'Удаляем одинаковые этапы... (Всего найдено: {len(set_to_remove)})')
        for resume in data:
            steps = resume.ITEMS
            try:steps.remove(next(step.db_id for step in steps for item in set_to_remove if item == step.db_id))
            except StopIteration: continue
    return data
