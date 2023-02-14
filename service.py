import datetime
from dateutil.relativedelta import relativedelta

relation = {
    0: 'не указано',
    1: 'не женат (не замужем)',
    2: 'встречается',
    3: 'помолвлен(-а)',
    4: 'женат (замужем)',
    5: 'всё сложно',
    6: 'в активном поиске',
    7: 'влюблен(-а)',
    8: 'в гражданском браке'
}

reversed_sex = {
    1: 2,
    2: 1
}


def get_age(date):
    date_strptime = datetime.datetime.strptime(date, '%d.%m.%Y')
    today = datetime.date.today()
    return relativedelta(today, date_strptime).years
