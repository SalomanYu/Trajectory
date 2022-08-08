import json
import logging
import settings

def detect_similar_trajectories(log:logging, resumes: list[settings.ResumeGroup]):
    res = []
    for current_index in range(len(resumes)):
        a = {
            "id": resumes[current_index].ID,
            "values": []
        }
        current_jobSteps = resumes[current_index].ITEMS        
        current_resumeName = current_jobSteps[0].name
        for comporable_index in range(current_index+1, len(resumes)):
            comporable_jobSteps = resumes[comporable_index].ITEMS 
            if len(current_jobSteps) == len(comporable_jobSteps):
                if [step.experience_post for step in current_jobSteps] == [step.experience_post for step in comporable_jobSteps]:
                    print('st')
                    log.info("Одинаковые пути ")
                    log.info("Одинаковые пути! %s -> %s", resumes[current_index].ID, resumes[comporable_index].ID)                    
                    
                        

if __name__ == "__main__":
    data = settings.load_resumes_json(settings.STEP_6_JSON_FILE)
    detect_similar_trajectories(data)