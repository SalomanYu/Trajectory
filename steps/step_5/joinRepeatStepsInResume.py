"""Здесь мы объединяем одинаковые этапы в карьере соискателя. Одинаковыми этапы считаются, если у них совпадают должности и отрасли на 100%"""

import logging
from rich.progress import track

import settings.tools as tools, settings.config as config
from settings.config import ResumeGroup
from steps.step_5.tools import merge_durations


def join_steps(log:logging, data: list[ResumeGroup]) -> tuple[list[ResumeGroup], set]:
    duplicate_set = set()
    for item in track(range(len(data)), description="[red]Объединение одинаковых этапов в карьере"):
        resume = data[item]
        carrerSteps = resume.ITEMS
        for step_one in range(1, len(carrerSteps)):
            step_one = step_one
            step_two = step_one - 1
            post_first = carrerSteps[step_one].experiencePost
            post_second = carrerSteps[step_two].experiencePost

            if post_first.lower() == post_second.lower():
                branch_first = carrerSteps[step_one].branch
                branch_second = carrerSteps[step_two].branch
                if branch_first.lower() == branch_second.lower() or len(branch_first) == 0 or len(branch_second) == 0:
                    log.info("Одинаковые этапы: %s --- %s", post_first, resume.ID)
                    merged_interval = ' — '.join((
                        carrerSteps[step_one].experienceInterval.split('—')[0],
                        carrerSteps[step_two].experienceInterval.split('—')[-1]))

                    merged_duration = merge_durations(carrerSteps, step_one, step_two)
                    duplicate_set.add(carrerSteps[step_one].db_id)
                    carrerSteps[step_one].experienceInterval = merged_interval
                    carrerSteps[step_one].experienceDuration = merged_duration

    return data, duplicate_set


def remove_repeat_steps(log:logging, data:list[ResumeGroup], set_to_remove:set) -> list[ResumeGroup]:
    if set_to_remove:
        log.warning("Было обнаружено %d повторяющихся дубликатов. Они будут объединены и удалены", len(set_to_remove))
        print(f'Удаляем одинаковые этапы... (Всего найдено: {len(set_to_remove)})')
        for item in set_to_remove:
            for resume in data:
                for step in resume.ITEMS:
                    if item == step.db_id: 

                        resume.ITEMS.remove(step)
                        log.warning("Deleted %d", step.db_id)
    return data


if __name__ == "__main__":
    log = tools.start_logging("step_5.log", folder="")
    data = tools.load_resumes_json(log=log, path=config.JSONFILE.STEP_4.value)
    resumes, duplicate_set = join_steps(log=log, data=data)
    resumes_without_duplicate_steps = remove_repeat_steps(log=log, data=resumes, set_to_remove=duplicate_set)
    tools.save_resumes_to_json(log=log, resumes=resumes_without_duplicate_steps, filename=config.JSONFILE.STEP_5.value)
