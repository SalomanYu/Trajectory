import numpy as np
import matplotlib.pyplot as plt

from config import DefaultLevelProfession, ProfessionStatistic, ProfessionWithSimilarResumes, ResumeGroup
from tools import experience_to_months, load_resumes_json



def create_plot(names:tuple, values: tuple, title:str) -> None:
    x_pos = np.arange(len(names))
    plt.bar(names, values, color = (0.5,0.1,0.5,0.6))

    plt.title(title)
    plt.xlabel('Профессии')
    plt.ylabel('Средний опыт')
    
    plt.xticks(x_pos, names)
    plt.show()


def show_vizualization_step_6(default_names:list[DefaultLevelProfession], statistic: list[ProfessionStatistic]) -> None:
    for proff in statistic:
        names = []
        values = []
        for deff in default_names:
            for lev in proff.levels:
                if deff.level == 0 and proff.prof_id == deff.profID: title = deff.name
                if deff.level == lev.level and proff.prof_id == deff.profID:
                    if lev.value == 0:
                        names.append(f"{deff.name}\nLev:{deff.level}(Без опыта)\nExp:{lev.value}")
                    else:
                        names.append(f"{deff.name}\nLev:{deff.level}\nExp:{lev.value}")
                    values.append(lev.value)
        create_plot(names, values, title)


def show_step_7(step_3_data: tuple[ResumeGroup], step_7_data: tuple[ResumeGroup]):
    groups_similar = []
    for current in range(len(step_7_data)):
        similar_set = set()
        current_resume = step_7_data[current]

        for comp in range(current+1, len(step_7_data)):
            comp_resume = step_7_data[comp]
            if comp_resume.ITEMS[0].similar_id == current_resume.ITEMS[0].similar_id:
                similar_set.add(comp_resume.ID)
        if similar_set: groups_similar.append(similar_set)
    
    
    
    # for group in groups_similar:
    group = groups_similar[0]

    for resume_step_3 in step_3_data:
        if resume_step_3.ID in group:
            first = ' -> '.join([step.experience_post + ":" + str(experience_to_months(step.experience_duration)) for step in resume_step_3.ITEMS])
            t1 = ":".join([step.experience_interval for step in resume_step_3.ITEMS])
            print(f"[ProffID:{resume_step_3.ITEMS[0].groupID}]\nDB_ID{resume_step_3.ITEMS[0].db_id}:{first} \n{t1}\n")
            for resume_step_7 in step_7_data:
                    if resume_step_7.ID == resume_step_3.ID:
                        if resume_step_7.ID in group:
                            second = ' -> '.join([step.resume.experience_post + ":" + str(experience_to_months(step.resume.experience_duration)) for step in resume_step_7.ITEMS])
                            t2 = ":".join([step.resume.experience_interval for step in resume_step_7.ITEMS])
                        
                            print(f"DB_ID:{resume_step_7.ITEMS[0].resume.db_id}: {second} \n{t2}\n------------------\n\n")
                            break   
        # break

def vizual_connect_between_steps(data: str, resumes: list[ResumeGroup] | list[ProfessionWithSimilarResumes]):
    data = [14,22,30,34,37,42,] #43,61,70,81,107,114,122,124,125,222,224,234,252,269,273,12231,12323,12324,12329]
    for resume in resumes:
        steps = resume.ITEMS
        if isinstance(steps[0], ProfessionWithSimilarResumes): steps = [item.resume for item in steps]
        for item in steps:
            if item.db_id == data[0]: 
                print(f"\n\t\t\t\t\t\tHeader: {item.experience_post}\n\n\n") 
                break

        if set([step.db_id for step in steps]) & set(data):
            print(steps[0].db_id, steps[0].url)
            print("    -->    ".join(step.experience_post for step in steps) + '\n\n------------------------------------------\n\n')


if __name__ == "__main__":
    ...
    # show_vizualization(names=defaul_names, values=data)