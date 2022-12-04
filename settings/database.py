import sqlite3

from settings.config import Connection, ProfessionStep, ResumeGroup, SimilarWay, CURRENT_DATABASE_NAME

def connect(db_name: str = CURRENT_DATABASE_NAME) -> Connection:
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    return Connection(db, cursor)

def create_table(table_name: str, db_name: str = CURRENT_DATABASE_NAME) -> None:
    db, cursor = connect(db_name)
    query = f"""CREATE TABLE IF NOT EXISTS {table_name}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(400),
        experiencePost VARCHAR(255),
        experienceInterval VARCHAR(100),
        experienceDuration VARCHAR(100),
        branch TEXT,
        subbranch TEXT,
        weightInGroup INTEGER,
        level INTEGER,
        levelInGroup INTEGER,
        groupId INTEGER,
        area VARCHAR(400),
        city VARCHAR(100),
        generalExperience VARCHAR (50),
        specialization TEXT,
        salary VARCHAR(255),
        educationUniversity TEXT,
        educationDirection TEXT,
        educationYear VARCHAR(50),
        languages TEXT,
        skills TEXT,
        advancedTrainingTitle TEXT,
        advancedTrainingDirection TEXT,
        advancedTrainingYear VARCHAR(50),
        dateUpdate DATE,
        resumeId TEXT,
        similarPathId INTEGER
    )"""
    cursor.execute(query)
    db.commit()
    db.close()

def get_all_resumes(table_name: str, db_name: str=CURRENT_DATABASE_NAME) -> tuple[ProfessionStep]:
    db, cursor = connect(db_name)
    cursor.execute(f"SELECT * FROM {table_name}")
    # (*item[1:], item[-1]) - Это значит, что мы берем сначала все значения стобцов, кроме первого
    # После этого мы в конец добавляем отдельно первый элемент. Такое решение используется потому,
    # что у ProfessionStep.db_id принимает дефолтное значение и поэтому мы поставиили его в конец
    data = (ProfessionStep(*(*item[1:], item[0])) for item in cursor.fetchall()) 
    db.close()
    return data

def add(table_name: str, data: ProfessionStep | list[ProfessionStep], db_name: str = CURRENT_DATABASE_NAME) -> None:
    """Надо разобраться почему я написал проверку снизу, ведь ProfessionStep это датакласс, у которого и так можно менять значения"""
    create_table(table_name, db_name)
    db, cursor = connect(db_name)
    if isinstance(data, list): column_count = len(data[0].__slots__) -1
    else: column_count = len(data.__slots__)-1
    
    query = f"""INSERT INTO {table_name}(title,experiencePost,experienceInterval,experienceDuration,
        branch,subbranch,weightInGroup ,level ,levelInGroup,groupId,area,city,generalExperience,specialization,salary,
        educationUniversity,educationDirection ,educationYear,languages ,skills,advancedTrainingTitle ,
        advancedTrainingDirection,advancedTrainingYear,dateUpdate,resumeId, similarPathId) 
        VALUES({','.join(('?' for _ in range(column_count)))})""" # Минус 1 так как нам не нужен айди в бд
    if isinstance(data, list):
        for row in data:
            cursor.execute(query, (row.title, row.experiencePost, row.experienceInterval, row.experienceDuration,
                row.branch, row.subbranch, row.levelInGroup, row.level, row.weightInGroup, row.groupId, row.area,
                row.city, row.generalExcepience, row.specialization, row.salary, row.educationUniversity,
                row.educationDirection, row.educationYear, row.languages, row.skills, row.advancedTrainingTitle,
                row.advancedTrainingDirection,row.advancedTrainingYear, row.dateUpdate, row.resumeId, 0))
            # print(row.title)
    else:
        cursor.execute(query, (data.title, data.experiencePost, data.experienceInterval, data.experienceDuration,
                data.branch, data.subbranch, data.levelInGroup, data.level, data.weightInGroup, data.groupId, data.area,
                data.city, data.generalExcepience, data.specialization, data.salary, data.educationUniversity,
                data.educationDirection, data.educationYear, data.languages, data.skills, data.advancedTrainingTitle,
                data.advancedTrainingDirection,data.advancedTrainingYear, data.dateUpdate, data.resumeId, 0))
        # print(data.title)
        
    db.commit()
    db.close()

def clear_table(tablename: str, db_name: str = CURRENT_DATABASE_NAME):
    db, cursor = connect(db_name)
    cursor.execute(f"DELETE FROM {tablename}")
    db.commit()
    print('Очищена таблица ', tablename)
    db.close()


def get_all_areas(tablename: str, db_name: str = CURRENT_DATABASE_NAME) -> list[str]:
    db, cursor = connect(db_name)
    cursor.execute(f"SELECT DISTINCT area FROM {tablename}")
    res = [area[0] for area in cursor.fetchall()]
    db.close()
    return res

def get_most_popular_work_way(table_name: str, db_name: str = CURRENT_DATABASE_NAME)-> tuple[ProfessionStep]:
    """Обращаемся к базе, данные которой прошли через все этапы построения путей и ищем профессию
    в заголовке резюме или в предыдущих должностях соискателя.
    Ищем наиболее повторяющиеся индефикаторы одинаковых путей.
    Возвращаем генератор списка, каждый элемент которого представляет собой строку из БД, 
    которая в свою очередь является отдельным этапом в карьере.
    Отделяются этапы разных резюме по resumeId, т.е ссылке на резюме 
    """

    db, cursor = connect(db_name)
    query = f"""SELECT DISTINCT resumeId, similarPathId FROM {table_name};"""
    cursor.execute(query)
    data = (SimilarWay(*item) for item in cursor.fetchall())
    
    distinct_ways = {} # Словарь вида Ключ-ID пути: Значение-Количество повторений
    for item in data:
        if item.similarId in distinct_ways: distinct_ways[item.similarId] += 1
        else: distinct_ways[item.similarId] = 1
    most_popular_similar_id = max(distinct_ways, key=distinct_ways.get) # Берем ключ максимального значения в словаре
    
    query = f"""SELECT * FROM {table_name} WHERE similarPathId={most_popular_similar_id}"""
    cursor.execute(query)
    db.close()
    return (ProfessionStep(*row[1:]) for row in cursor.fetchall())


def find_profession_in_work_ways(profession_name: str, table_name: str, db_name: str = CURRENT_DATABASE_NAME)\
     -> tuple[ProfessionStep] | None:
    """Обращаемся к базе, данные которой прошли через все этапы построения путей и ищем профессию
    в заголовке резюме или в предыдущих должностях соискателя.
    Если такая профессия есть в БД, то вернется генератор списка, содержащий все совпадения с профессией
    Замечание: В поиске не учитывается пунктуация и регистр
    """
        
    db, cursor = connect(db_name)
    query = f"""SELECT * FROM {table_name} 
        WHERE title='{profession_name}' OR experiencePost='{profession_name}'"""
    cursor.execute(query)
    data = (ProfessionStep(*item[1:]) for item in cursor.fetchall())
    db.close()
    if data: 
        return data
    return None


def get_resume_by(tablename: str, similarPathId:int=None, area:str=None, resumeId:str=None, professionName:str=None, db_name: str = CURRENT_DATABASE_NAME) -> ResumeGroup:
    """Нужно выбрать один из предложенных аргументов. Если хотите найти резюме по similarPathId, то area является так же обязательным полем"""
    if similarPathId and area: query = f"SELECT * FROM {tablename} WHERE similarPathId={similarPathId} AND area='{area}'"
    elif resumeId: query = f"SELECT * FROM {tablename} WHERE resumeId='{resumeId}'"
    elif professionName: query = f"SELECT * FROM {tablename} WHERE title='{professionName}' OR experiencePost='{professionName}'"
    else: raise SyntaxError("Вы должны передать в функцию хотя бы один параметр")

    db, cursor = connect(db_name)
    cursor.execute(query)
    id = ProfessionStep(*cursor.fetchone()[1:]).resumeId
    cursor.execute(f"SELECT * FROM {tablename} WHERE resumeId='{id}'")   
    return ResumeGroup(ID=id, ITEMS=[ProfessionStep(*(*step[1:], step[0])) for step in cursor.fetchall()]) 
    

def save_final_result_to_db(similared_workways: list[ResumeGroup]) -> None:
    # clear_table('New')
    create_table("resumes")
    for resume in similared_workways:
        for step in resume.ITEMS: add(table_name='resumes', data=step)
