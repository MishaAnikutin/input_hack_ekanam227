import pandas as pd
from tqdm import tqdm
import time
from function import *

class NewsPreprocessing:
    """
    Класс для предобработки новостных данных, включая:
    - преобразование даты и URL
    - генерацию суммаризации текстов
    - анализ тональности (сентимента)
    - загрузку обработанных данных в БД
    """
    
    def __init__(self, client, db):
        """
        Инициализация обработчика новостей
        
        Параметры:
            df (pd.DataFrame): Исходный DataFrame с новостями
            client: Клиент для работы с API (например, для запросов суммаризации/сентимента)
            db: Объект для работы с базой данных
        """
        self.db = db
        self.client = client

    def get_data(self,batch:pd.DataFrame):
        """
        batch - это часть batch
        Базовая предобработка данных:
        1. Конвертация даты в datetime формат
        2. Переименование колонки URL -> url
        """
        self.df = batch
        self.df["date"] = pd.to_datetime(self.df["date"])  # Конвертируем в datetime
        self.df.rename(columns={"URL": "url"}, inplace=True)  # Стандартизируем название колонки

    def get_sentiment(self):
        """
        Анализ тональности текста (сентимента):
        1. Проверяет, что суммаризация выполнена
        2. Для каждого текста получает сентимент через API
        3. Результат парсит и сохраняет в колонки:
           - market_sentiment (int): -1, 0 или 1
           - probability (float): вероятность/интенсивность сентимента
        
        Возвращает:
            pd.DataFrame с результатами анализа
            
        Вызывает:
            ValueError: если не выполнена суммаризация текстов
        """
        if self.df['summary_text'].isnull().any():
            raise ValueError("Сначала выполните get_summary()")
        
        def get_resp_sent(text): #Фигня чтобы возвращал
            time.sleep(0.09)
            try:
                return eval(get_response(prompt_for_sentiment(text), self.client))
            except:
                print('Спорная тема')
                return 0
        
        
        
        sentiment = self.df["summary_text"].apply(get_resp_sent)
        self.df[['market_sentiment', 'probability']] = sentiment.tolist()
        self.df['market_sentiment'] = self.df['market_sentiment'].astype(int)
        self.df['probability'] = self.df['probability'].astype(float)
        self.df['probability'] = self.df['probability'] * self.df['market_sentiment']
        pd.DataFrame(sentiment.tolist())
        
        return pd.DataFrame(sentiment.tolist())  # Возвращаем сырые данные

    def get_summary(self):
        """
        Генерация суммаризации новостей:
        1. Для каждого текста получает краткое содержание через API
        2. Сохраняет результат в колонку summary_text
        
        Возвращает:
            Series с суммаризациями
        """
        def get_resp_sum(text): #Фигня чтобы возвращал
            time.sleep(0.09)
            try:
                return get_response(prompt_for_summarization(text), self.client)
            except:
                print('Спорная тема')
                return 'Политическая и очень спорная тема'
        
        sum_text = self.df["text"].apply(get_resp_sum)
        self.df["summary_text"] = sum_text  # Сохраняем результат
        return sum_text  # Возвращаем суммаризации
    
    def process_tickers_whole_df(self,text_column: str = 'text',ticker_column: str = 'ticker',delay: float = 0.1) -> pd.DataFrame:
    # Функция для обработки одного текста
        def process_single_text(text):
            try:
                prompt = prompt_for_ticker(text)
                response = get_response(prompt, client_params)
                time.sleep(delay)  # Задержка между запросами
                return eval(response) if response else []
            except Exception as e:
                print(f"Ошибка обработки текста: {str(e)}")
                return []
    
    # Включаем прогресс-бар для apply
        tqdm.pandas(desc="Processing texts")
    
    # Применяем функцию ко всем текстам
        self.df[ticker_column] = self.df[text_column].progress_apply(process_single_text)
    
        return self.df

    def load_data(self, similarity_threshold):
        """
        Загрузка обработанных данных в базу данных
        
        Параметры:
            similarity_threshold: Порог схожести для проверки дубликатов
        """
        self.db.upload(self.df, similarity_threshold)  # Делегируем загрузку DB-модулю