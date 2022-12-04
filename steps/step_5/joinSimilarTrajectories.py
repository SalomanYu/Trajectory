from loguru import logger
from settings.config import ResumeGroup, ProfessionStep
from rich.progress import track
from typing import NamedTuple


class ComparisonStepInfo(NamedTuple):
    Post    :str
    Branch  :str

class ComparisonResumeInfo(NamedTuple):
    StepsCount  :int
    Steps       :list[ComparisonStepInfo]


def detect_similar_workWays(resumes: list[ResumeGroup]):
    similar_set = set()
    similar_id_count = 0

    for current in track(range(len(resumes)), description="[yellow]Определение схожих путей"):
        similar_id_count += 1
        current_steps = resumes[current].ITEMS
        if resumes[current].ID not in similar_set:
            for step in current_steps: step.similarPathId = {similar_id_count} # Множество, т.к нам нужен был изменняемый тип данных в NamedTuple

        for comporable in range(current+1, len(resumes)):
            comporable_steps = resumes[comporable].ITEMS
            if len(current_steps) == len(comporable_steps) and current_steps[0].title == comporable_steps[0].title:
                current_career_jobs = [step.experiencePost for step in current_steps]                    
                comporable_career_jobs = [step.experiencePost for step in comporable_steps]                    

                current_career_jobs_branches = [step.branch for step in current_steps]
                comporable_career_jobs_branches = [step.branch for step in comporable_steps]
                if (current_career_jobs == comporable_career_jobs) and (current_career_jobs_branches == comporable_career_jobs_branches):
                    if resumes[comporable].ID not in similar_set:

                        for step in current_steps: step.similarPathId = {similar_id_count}
                        similar_set.add(resumes[comporable].ID)
                        logger.info(f"Одинаковые пути! {resumes[current].ID} -> {resumes[comporable].ID}")                    
    return resumes


def check_similarity_between_two_resumes(resume1: ResumeGroup, resume2: ResumeGroup):
    ...


def get_comparison_resume_info(resume:ResumeGroup):
    steps = get_comparison_steps_info(resume.ITEMS)
    return ComparisonResumeInfo(
        StepsCount=len(resume.ITEMS),
        Steps=steps
    )

def get_comparison_steps_info(steps: list[ProfessionStep]) -> list[ComparisonStepInfo]:
    steps_: list[ComparisonStepInfo] = []
    for step in steps:
        steps_.append(ComparisonStepInfo(
            Post=step.experiencePost,
            Branch=step.experiencePost
        ))
    return steps_