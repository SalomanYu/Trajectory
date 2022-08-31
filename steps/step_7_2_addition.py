import logging
from pprint import pprint
from config import *
from tools import load_resumes_json, start_logging

from typing import NamedTuple

class SimilarWay(NamedTuple):
    way_id: int
    count_ways: int

def find_most_popular_workWay(log):
    data = load_resumes_json(path=JSONFILE.STEP_7.value, log=log, is_seven_step=True)
    similar_id_nums = [resume.ITEMS[0].similar_id for resume in data]
    test_dict = {}
    for similar_id in similar_id_nums:
        test_dict[similar_id] = similar_id_nums.count(similar_id)

    most_popular_ways = []
    for key, value in test_dict.items():
        most_popular_ways.append(SimilarWay(way_id=key, count_ways=value))
    
    max_ways = SimilarWay(way_id=0, count_ways=0)
    max_len = 0
    for way in most_popular_ways:
        if way.count_ways > max_ways.count_ways and len(get_jobSteps_like_workWay(data, similar_id=way.way_id)) >= max_len:
            max_ways = way
            max_len = len(get_jobSteps_like_workWay(data, similar_id=way.way_id))
    print(max_ways)


    

def get_jobSteps_like_workWay(data, similar_id: int) -> list[WorkWay]:
    try:
        resume = [resume.ITEMS for resume in data if resume.ITEMS[0].similar_id == similar_id][0]
    except:
        exit("[Ошибка] Не найден индефикатор одинаковых путей в файле JSON/STEP_7...")
    
    
    work_way = [WorkWay(post=item.resume.experience_post, brach=item.resume.branch, level=get_level_by_postName(item.resume.experience_post)) for item in resume]
    
    return work_way #+ [resume[0].resume.url]


def get_level_by_postName(experience_post: ResumeProfessionItem.experience_post) -> 0 | 1 | 2 | 3 | 4:
    for lev in LEVEL_KEYWORDS:
        if lev.key_words & set(experience_post.split()): return lev.level
    return 0


if __name__ == "__main__":
    find_most_popular_workWay()