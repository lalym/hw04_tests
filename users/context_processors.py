import datetime as dt


def year():
    """
    Добавляет переменную с текущим годом.
    """
    return {
        "year": dt.datetime.today().year
    }
