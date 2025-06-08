from datetime import datetime


def custom_date_parser(date_str: str) -> datetime:
    """
    Парсит строку формата [HH:MM, day month_year] с русским названием месяца
    Пример: "[00:30, 7 июня 2025]" → datetime(2025, 6, 7, 0, 30)
    """
    # Удаляем квадратные скобки и лишние пробелы
    clean_str = date_str.strip('[]')
    
    # Словарь для преобразования русских месяцев
    months = {
        'января': 1, 'февраля': 2, 'марта': 3,
        'апреля': 4, 'мая': 5, 'июня': 6,
        'июля': 7, 'августа': 8, 'сентября': 9,
        'октября': 10, 'ноября': 11, 'декабря': 12
    }
    
    # Разбиваем на составляющие
    time_part, date_part = clean_str.split(', ')
    hours, minutes = map(int, time_part.split(':'))
    day, month_ru, year = date_part.split()
    
    return datetime(
        year=int(year),
        month=months[month_ru.lower()],
        day=int(day),
        hour=hours,
        minute=minutes
    )
