import json
import logging
from config import ResumeGroup, ProfessionWithSimilarResumes
import tools, config
from rich.progress import track


def detect_similar_workWays(log:logging, resumes: list[ResumeGroup]):
    similar_set = set()
    result_similar_resume_list = []
    similar_id_count = 0

    for current in track(range(len(resumes)), description="[yellow]Определение схожих путей"):
        similar_id_count += 1
        current_steps = resumes[current].ITEMS

        if resumes[current].ID not in similar_set:
            result_similar_resume_list.append(ProfessionWithSimilarResumes(resume=resumes[current], similar_id=similar_id_count))

        for comporable in range(current+1, len(resumes)):
            comporable_steps = resumes[comporable].ITEMS
        
            if len(current_steps) == len(comporable_steps):
                current_career_jobs = [step.experience_post for step in current_steps]                    
                comporable_career_jobs = [step.experience_post for step in comporable_steps]                    

                current_career_jobs_branches = [step.branch for step in current_steps]
                comporable_career_jobs_branches = [step.branch for step in comporable_steps]

                if (current_career_jobs == comporable_career_jobs) and (current_career_jobs_branches == comporable_career_jobs_branches):
                    if resumes[comporable].ID not in similar_set:

                        result_similar_resume_list.append(ProfessionWithSimilarResumes(resume=resumes[comporable], similar_id=similar_id_count))
                        similar_set.add(resumes[comporable].ID)

                        log.info("Одинаковые пути! %s -> %s", resumes[current].ID, resumes[comporable].ID)                    
    tools.save_resumes_to_json(log=log, resumes=result_similar_resume_list, filename=config.STEP_7_JSON_FILE, is_seven_step=True)
    

if __name__ == "__main__":
    data = tools.load_resumes_json(config.STEP_6_JSON_FILE)
    detect_similar_workWays(data)