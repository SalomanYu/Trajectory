from settings.database import get_all_resumes, add, clear_table
from settings.config import ProfessionStep, ResumeGroup
from settings.tools import group_steps_to_resume
import locale
from typing import NamedTuple
from operator import attrgetter
from datetime import datetime, date
from rich.progress import track
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


datetime.strptime


MonthDict = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
    "january": 1,
    "february":2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

class interval(NamedTuple):
    step: ProfessionStep
    start_date: date

# steps = set(['Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июнь 2001 — Июль 2010', 'Июль 2015 — Март 2016', 'Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июнь 2001 — Июль 2010', 'Июль 2015 — Март 2016', 'Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июнь 2001 — Июль 2010', 'Июль 2015 — Март 2016', 'Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июнь 2001 — Июль 2010', 'Июль 2015 — Март 2016', 'Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июнь 2001 — Июль 2010', 'Июль 2015 — Март 2016', 'Июль 2014 — Май 2015', 'Июль 2010 — Февраль 2012', 'Февраль 2012 — Июнь 2014', 'Июнь 2016 — по настоящее время', 'Июль 2015 — Март 2016'])

def sort_steps(steps: list[ProfessionStep]) -> list[ProfessionStep]:
    intervals = []
    for step in steps:
        step_start = step.experienceInterval.split(" — ")[0]
        if not step_start: continue
        try:
            start_year = step_start.split()[-1]
        except:
            exit(f"Err:{step.experienceInterval}")
        start_month = next(k for i, k in MonthDict.items() if i==step_start.split()[0].lower())
        start_date = datetime.strptime(f"{start_month}.{start_year}", "%m.%Y")
        intervals.append(interval(step, start_date))
    return [interval.step for interval in sorted(intervals, key=attrgetter("start_date"))]

resumes = group_steps_to_resume(get_all_resumes("New"))
for resume in track(range(len(resumes)), description="[red]Осталось:"):
    sorded_steps = sort_steps(resumes[resume].ITEMS)
    resumes[resume].ITEMS = sorded_steps


clear_table('New')
print("записываем в бд")
for resume in resumes:
    for step in resume.ITEMS:
        add(table_name='New', data=step)