import logging
from pprint import pprint
from config import *
from tools import load_resumes_json, start_logging

def find_most_popular_workWay(log):
    data = load_resumes_json(path=STEP_7_JSON_FILE, log=log, is_seven_step=True)
    similar_id_nums = [resume.ITEMS[0].similar_id for resume in data]
    most_popular_dict = {}
    for id_ in similar_id_nums:
        most_popular_dict[str(id_)] = similar_id_nums.count(id_)
    
    count_similar_workWays = len([value for _, value in most_popular_dict.items() if value > 1])
    most_popular_way = max(most_popular_dict, key=most_popular_dict.get)

    for key, value in most_popular_dict.items():
        if value > 1:
            ways = get_jobSteps_like_workWay(data, similar_id=int(key))
            if len(ways) > 2:
                print("Count:", value)
                pprint(ways)
                print()

    # return get_jobSteps_like_workWay(data, similar_id=int(most_popular_way))
    

def get_jobSteps_like_workWay(data, similar_id: int) -> list[WorkWay]:
    try:
        resume = [resume.ITEMS for resume in data if resume.ITEMS[0].similar_id == similar_id][0]
    except:
        exit("[Ошибка] Не найден индефикатор одинаковых путей в файле JSON/STEP_7...")
    
    
    work_way = [WorkWay(post=item.resume.experience_post, brach=item.resume.branch, level=get_level_by_postName(item.resume.experience_post)) for item in resume]
    return work_way

def get_level_by_postName(experience_post: ResumeProfessionItem.experience_post) -> 0 | 1 | 2 | 3 | 4:
    for lev in LEVEL_KEYWORDS:
        if lev.key_words & set(experience_post.split()): return lev.level
    return 0


if __name__ == "__main__":
    find_most_popular_workWay()