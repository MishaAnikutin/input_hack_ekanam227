import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import requests 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.path.append('c:\\Users\\a.n.piskunov\\Desktop\\gitlab\\input_hack_ekanam227')
from backend.tasks.date_parser import custom_date_parser
from backend.tasks.Lenta_parser import LentaNewsParser
from backend.tasks.Rbc_parser import rbc_parser

class NewsParser:
    def __init__(self, base_url: str = 'https://lenta.ru', max_workers: int = 10,
                 user_agent: str = None, csv_file: str = 'news_data.csv'):
        self.lenta_parser = LentaNewsParser(base_url, max_workers, user_agent)
        self.rbc_parser = rbc_parser()
        self.CSV_FILE = csv_file
        self._init_csv_structure()

    def _init_csv_structure(self):
        """Инициализирует файл CSV с созданием необходимых директорий"""
        try:
            Path(self.CSV_FILE).parent.mkdir(parents=True, exist_ok=True)
            pd.read_csv(self.CSV_FILE)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            pd.DataFrame(columns=['text', 'title', 'url', 'date', 'source']).to_csv(
                self.CSV_FILE, index=False)

    def parse_daily(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        """Парсинг новостей за определенный период времени"""
        # Обработка данных Lenta
        try:
            lenta_data = self.lenta_parser.parse_date_range(start_date, end_date)
            if 'date' in lenta_data.columns and not lenta_data.empty:
                lenta_data['date'] = lenta_data['date'].apply(
                    lambda x: custom_date_parser(x) if x else datetime.now()
                )
            else:
                print("Warning: Нет данных от LentaNews")
                lenta_data = pd.DataFrame()
        except Exception as e:
            print(f"Ошибка парсинга Lenta: {str(e)}")
            lenta_data = pd.DataFrame()

        # Обработка данных RBC с проверкой дат
        rbc_data = pd.DataFrame()
        try:
            end_date = end_date or datetime.now().strftime('%Y-%m-%d')
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

            # Автокорректировка дат если start_date > end_date
            if start_date_dt > end_date_dt:
                start_date_dt, end_date_dt = end_date_dt - timedelta(days=1), end_date_dt
                print(f"Автокорректировка дат для RBC: {start_date} -> {start_date_dt.strftime('%Y-%m-%d')}")

            rbc_param_dict = {
                'project': 'rbcnews',
                'category': 'TopRbcRu_economics',
                'dateFrom': start_date_dt.strftime('%d.%m.%Y'),
                'dateTo': end_date_dt.strftime('%d.%m.%Y'),
                'query': 'РБК',
                'page': '1',
                'material': 'news'
            }
            rbc_data = self.rbc_parser.get_articles(rbc_param_dict, save_excel=False)
            rbc_data = self.rbc_parser.extract_relevant_data(rbc_data)
        except ValueError as e:
            print(f"Ошибка RBC (пропускаем): {str(e)}")
        except Exception as e:
            print(f"Критическая ошибка RBC: {str(e)}")

        # Объединение данных с проверкой на пустые DataFrame
        frames = [df for df in [lenta_data, rbc_data] if not df.empty]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def parse_new(self) -> pd.DataFrame:
        """Парсинг новых новостей с сохранением в указанный CSV"""
        try:
            existing_data = pd.read_csv(self.CSV_FILE)
            existing_data['date'] = pd.to_datetime(
                existing_data['date'], 
                format='%d.%m.%Y %H:%M:%S',
                errors='coerce'
            )
            existing_data = existing_data[~existing_data['date'].isna()]
            
            if not existing_data.empty:
                last_date = existing_data['date'].max().strftime('%Y-%m-%d')
            else:
                last_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                
        except (FileNotFoundError, KeyError, pd.errors.EmptyDataError) as e:
            print(f"Инициализация нового файла: {str(e)}")
            existing_data = pd.DataFrame()
            last_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        # Проверка и корректировка last_date
        current_date = datetime.now().date()
        try:
            last_date_obj = datetime.strptime(last_date, "%Y-%m-%d").date()
            if last_date_obj > current_date:
                last_date = current_date.strftime("%Y-%m-%d")
                print(f"Корректировка last_date на текущую дату")
        except:
            last_date = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")

        new_data = self.parse_daily(last_date, datetime.now().strftime('%Y-%m-%d'))
        
        # Фильтрация дубликатов
        if not existing_data.empty and not new_data.empty:
            new_data = new_data[~new_data['url'].isin(existing_data['url'])]
        
        # Сохранение данных
        if not new_data.empty:
            combined = pd.concat([existing_data, new_data], ignore_index=True)
            combined['date'] = pd.to_datetime(combined['date']).dt.strftime('%d.%m.%Y %H:%M:%S')
            combined.to_csv(self.CSV_FILE, index=False)
            print(f"Добавлено {len(new_data)} новых записей")
        else:
            print("Нет новых данных для добавления")

        return new_data
