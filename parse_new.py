import os
import json
import pandas as pd
import subprocess
from datetime import datetime

def parse_daily(channel, date=None):
    """Парсит посты из канала начиная с указанной даты (если None - парсит все)"""
    if date:
        date_str = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
        command = f"snscrape --since {date_str} --jsonl telegram-channel {channel} > {channel}_temp.txt"
    else:
        command = f"snscrape --since 2025-05-08 --jsonl telegram-channel {channel} > {channel}_temp.txt"
    subprocess.run(command, shell=True)

def transform_file(filename, channel):
    """Преобразует сырые данные из файла в список словарей"""
    posts = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return posts
    n = 0
    for line in lines:
        try:
            data = json.loads(line.strip())
            post = {
                'text': data['content'],
                'title': n,  # или другая логика для title
                'url': data['url'],
                'date': data['date'],
                'source': f"tg_{channel}"
            }
            posts.append(post)
        except (json.JSONDecodeError, KeyError):
            continue
        n += 1
    return posts

def parse_new(channel):
    # Определение путей к файлам
    csv_file = f"{channel}.csv"
    temp_file = f"{channel}_temp.txt"
    
    # Проверка существования CSV
    if os.path.exists(csv_file):
        df_old = pd.read_csv(csv_file)
        # Конвертируем даты и находим последнюю
        df_old['date'] = pd.to_datetime(df_old['date'])
        last_date = df_old['date'].max().strftime('%Y-%m-%d')
    else:
        df_old = pd.DataFrame(columns=['text', 'title', 'url', 'date', 'source'])
        last_date = None

    # Парсинг новых данных (начиная с последней даты)
    parse_daily(channel, last_date)
    new_posts = transform_file(temp_file, channel)
    
    # Удаление временного файла
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    if not new_posts:
        print("Новых постов не найдено.")
        return

    # Создаем DataFrame для новых данных
    df_new = pd.DataFrame(new_posts)
    df_new['date'] = pd.to_datetime(df_new['date'])
    
    # Объединяем старые и новые данные
    df_combined = pd.concat([df_new, df_old], ignore_index=True)
    
    # Удаляем дубликаты по URL и сохраняем
    df_combined = df_combined.drop_duplicates(subset='url', keep='first')
    df_combined.to_csv(csv_file, index=False)
    print(f"Добавлено новых постов: {len(df_new)}. Итоговое количество: {len(df_combined)}")

# Пример использования
parse_new("institut_gaidara")
