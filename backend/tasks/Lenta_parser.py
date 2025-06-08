import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import pandas as pd

class LentaNewsParser:
    def __init__(self, base_url: str = 'https://lenta.ru', max_workers: int = 10, user_agent: str = None):
        self.BASE_URL = base_url
        self.MAX_WORKERS = max_workers
        self.USER_AGENT = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
    def parse_date_range(self, start_date: str, end_date: str = None) -> list:
        """Основной метод для парсинга новостей за период"""
        results = []
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            
            current_dt = start_dt
            while current_dt <= end_dt:
                self._process_date(current_dt, executor, futures)
                current_dt += timedelta(days=1)

            # Собираем результаты
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        return pd.DataFrame(results)

    def _process_date(self, date: datetime, executor: ThreadPoolExecutor, futures: list):
        """Обработка одной даты"""
        page = 1
        while True:
            news_page_url = f"{self.BASE_URL}/news/{date.year}/{date.month:02d}/{date.day:02d}/page/{page}/"
            print(f"Checking: {news_page_url}")
            
            try:
                response = requests.get(news_page_url, headers={'User-Agent': self.USER_AGENT})
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                news_items = soup.find_all('a', class_=['card-full-news', 'card-mini-news'])
                
                if not news_items:
                    break
                    
                for item in news_items:
                    news_url = urljoin(self.BASE_URL, item['href'])
                    futures.append(executor.submit(self._parse_single_news, news_url))
                
                page += 1
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    break
                print(f"HTTP Error {e.response.status_code}: {news_page_url}")
                break
            except Exception as e:
                print(f"Error processing {news_page_url}: {str(e)}")
                break

    def _parse_single_news(self, url: str) -> dict:
        """Парсинг отдельной новости"""
        try:
            time.sleep(0.5)  # Защита от слишком частых запросов
            response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            return {
                'text': self._extract_content(soup),
                'title': self._extract_title(soup),
                'url': url,
                'date': self._extract_time(soup),
                'source': 'LENTA.RU'
            }
        except Exception as e:
            print(f"Error parsing {url}: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Извлечение заголовка"""
        title_tag = soup.find('h1', class_='topic-body__title') or soup.find('span', class_='topic-body__title')
        return title_tag.text.strip() if title_tag else 'No title'

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Извлечение текста новости"""
        content_div = soup.find('div', class_='topic-body__content') or soup.find('div', class_='topic-body__content-text')
        return ' '.join([p.text for p in content_div.find_all('p')]) if content_div else 'No content'

    def _extract_time(self, soup: BeautifulSoup) -> str:
        """Извлечение времени публикации"""
        time_tag = soup.find('a', class_=lambda x: x and {'topic-header__item', 'topic-header__time'}.issubset(x.split()))
        return time_tag.text.strip() if time_tag else None