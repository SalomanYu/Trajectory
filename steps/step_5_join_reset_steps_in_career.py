"""Здесь мы объединяем одинаковые этапы в карьере соискателя. Одинаковыми этапы считаются, если у них совпадают должности и отрасли на 100%"""

import logging
import re
import settings
from settings import ResumeGroup

def join_steps(log:logging, data: list[ResumeGroup]) -> tuple[list[ResumeGroup], set]:
    duplicate_set = set()
    for resume in data:
        carrerSteps = resume.ITEMS
        for step_one in range(1, len(carrerSteps)):
            step_one = step_one
            step_two = step_one - 1
            post_first = carrerSteps[step_one].experience_post
            post_second = carrerSteps[step_two].experience_post

            if post_first.lower() == post_second.lower():
                branch_first = carrerSteps[step_one].branch
                branch_second = carrerSteps[step_two].branch

                if branch_first.lower() == branch_second.lower():
                    print(carrerSteps[step_one].db_id, carrerSteps[step_two].db_id)
                    log.info("Одинаковые этапы: %s %s", post_first, resume.ID)
                    merged_interval = ' — '.join((
                        carrerSteps[step_one].experience_interval.split('—')[0],
                        carrerSteps[step_two].experience_interval.split('—')[-1]))

                    merged_duration = merge_durations(carrerSteps, step_one, step_two)
                    duplicate_set.add(carrerSteps[step_one].db_id)
                    carrerSteps[step_one].experience_interval = merged_interval
                    print(f"\tПервый: {carrerSteps[step_one].experience_duration} + Второй:{carrerSteps[step_two].experience_duration} -> {merged_duration} ({merged_interval})")
                    carrerSteps[step_one].experience_duration = merged_duration

    return data, duplicate_set

def merge_durations(carrerSteps:list, step_one:int, step_two:int) -> str:
    # Обрезаем лишние пробелы у строк (Метод strip() не помог)
    duration_first = ' '.join(
        carrerSteps[step_one].experience_duration.split())
    # Обрезаем лишние пробелы у строк (Метод strip() не помог)
    duration_second = ' '.join(
        carrerSteps[step_two].experience_duration.split())

    month_pattern = '\d{2} м|\d{2} m|\d м|\d m'
    year_pattern = '\d{2} г|\d{2} y|\d г|\d y|\d{2} л'
    try:
        months_first = int(re.findall(month_pattern, duration_first)[0].split(' ')[0])
    except IndexError:
        months_first = 0
    try:
        months_second = int(re.findall(month_pattern, duration_second)[0].split(' ')[0])
    except IndexError:
        months_second = 0
    try:
        years_first = int(re.findall(year_pattern, duration_first)[0].split(' ')[0])
    except IndexError:
        years_first = 0
    try:
        years_second = int(re.findall(year_pattern, duration_second)[0].split(' ')[0])
    except IndexError:
        years_second = 0

    # Делим на 12, потому что у нас 12 система счисления
    total_months = (months_first + months_second) % 12
    # Делим на 12, потому что у нас 12 система счисления
    total_years = years_first + years_second + \
        ((months_first + months_second) // 12)

    final_date = get_current_date(
        years=str(total_years), months=str(total_months))

    return final_date

def get_current_date(years: str, months: str) -> str:
    if months == '1': month_type = 'месяц'
    elif months in ('2', '3', '4'): month_type = 'месяца'
    else: month_type = 'месяцев'

    if years != '11' and str(years)[-1] == '1': year_type = 'год'
    elif years not in ('12', '13', '14') and str(years)[-1] in ('2', '3', '4'): year_type = 'года'
    else: year_type = 'лет'

    if years == '0': return ' '.join((months, month_type))
    elif months == '0': return ' '.join((years, year_type))

    return ' '.join((years, year_type, months, month_type))

def remove_repeat_steps(log:logging, data:list[ResumeGroup], set_to_remove:set) -> list[ResumeGroup]:
    if set_to_remove:
        log.warning("Было обнаружено %d повторяющихся дубликатов. Они будут объединены и удалены", len(set_to_remove))
        for item in set_to_remove:
            for resume in data:
                for step in resume.ITEMS:
                    if item == step.db_id: 
                        resume.ITEMS.remove(step)
                        log.warning("Deleted %d", step.db_id)
    return data


if __name__ == "__main__":
    log = settings.start_logging("step_5.log", folder="")
    data = settings.load_resumes_json(log=log, path=settings.STEP_4_JSON_FILE)
    resumes, duplicate_set = join_steps(log=log, data=data)
    resumes_without_duplicate_steps = remove_repeat_steps(log=log, data=resumes, set_to_remove=duplicate_set)
    settings.save_resumes_to_json(log=log, resumes=resumes_without_duplicate_steps, filename=settings.STEP_5_JSON_FILE)
