import re

from settings.config import ProfessionStep


def merge_durations(carrerSteps:list[ProfessionStep], step_one:int, step_two:int) -> str:
    # Обрезаем лишние пробелы у строк (Метод strip() не помог)
    duration_first = ' '.join(carrerSteps[step_one].experienceDuration.split())
    duration_second = ' '.join(carrerSteps[step_two].experienceDuration.split())

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

    final_date = __get_current_date(
        years=str(total_years), months=str(total_months))

    return final_date

def __get_current_date(years: str, months: str) -> str:
    if months == '1': month_type = 'месяц'
    elif months in ('2', '3', '4'): month_type = 'месяца'
    else: month_type = 'месяцев'

    if years != '11' and str(years)[-1] == '1': year_type = 'год'
    elif years not in ('12', '13', '14') and str(years)[-1] in ('2', '3', '4'): year_type = 'года'
    else: year_type = 'лет'

    if years == '0': return ' '.join((months, month_type))
    elif months == '0': return ' '.join((years, year_type))

    return ' '.join((years, year_type, months, month_type))