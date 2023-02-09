import datetime

from dateutil.relativedelta import relativedelta


sex_table = {
    0: 'любой',
    1: 'женский',
    2: 'мужской',
}

reversed_sex_table = {
    1: 2,
    2: 1,
}

relation_table = {
    0: 'не указано',
    1: 'не женат (не замужем)',
    2: 'встречается',
    3: 'помолвлен(-а)',
    4: 'женат (замужем)',
    5: 'всё сложно',
    6: 'в активном поиске',
    7: 'влюблен(-а)',
    8: 'в гражданском браке',
}


def get_age(date: str) -> int:
    date_object = datetime.datetime.strptime(date, '%d.%m.%Y')
    today = datetime.date.today()
    return relativedelta(today, date_object).years
