from settings.config import DEFAULT_VALUES

def get_default_average_value(statistic:list[int, int], level:int) -> int:
    if statistic: return round(statistic[0] / statistic[1])
    else: return DEFAULT_VALUES[level]