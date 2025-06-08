import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from IPython.display import display, clear_output

class rbc_parser:
    def __init__(self):
        pass
    
    
    def _get_url(self, param_dict: dict) -> str:
        """
        Возвращает URL для запроса json таблицы со статьями
        """
        url = 'https://www.rbc.ru/search/ajax/?' +\
        'project={0}&'.format(param_dict['project']) +\
        'category={0}&'.format(param_dict['category']) +\
        'dateFrom={0}&'.format(param_dict['dateFrom']) +\
        'dateTo={0}&'.format(param_dict['dateTo']) +\
        'page={0}&'.format(param_dict['page']) +\
        'query={0}&'.format(param_dict['query']) +\
        'material={0}'.format(param_dict['material'])
        
        # 'offset={0}&'.format(param_dict['offset']) +\
        # 'limit={0}&'.format(param_dict['limit']) +\
        
        return url
    
    
    def _get_search_table(self, param_dict: dict,
                          include_text: bool = True) -> pd.DataFrame:
        """
        Возвращает pd.DataFrame со списком статей
        
        include_text: bool
        ### Если True, статьи возвращаются с текстами
        """
        url = self._get_url(param_dict)
        r = requests.get(url)
        search_table = pd.DataFrame(r.json()['items'])
        if include_text and not search_table.empty:
            get_text = lambda x: self._get_article_data(x['fronturl'])
            search_table[['overview', 'text']] = search_table.apply(get_text,
                                                                    axis=1).tolist()
        
        if 'publish_date_t' in search_table.columns:
            search_table.sort_values('publish_date_t', ignore_index=True)
            
        return search_table
    
    
    def _iterable_load_by_page(self, param_dict):
        param_copy = param_dict.copy()
        results = []
        
        page = 1
        while True:
            param_copy['page'] = str(page)
            result = self._get_search_table(param_copy)
            if result.empty:
                break
            results.append(result)
            page += 1
        
        results = pd.concat(results, axis=0, ignore_index=True)
        
        return results
    
    
    def _get_article_data(self, url: str):
        """
        Возвращает описание и текст статьи по ссылке
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="lxml") # features="lxml" чтобы не было warning
        div_overview = soup.find('div', {'class': 'article__text__overview'})
        if div_overview:
            overview = div_overview.text.replace('<br />','\n').strip()
        else:
            overview = None
        p_text = soup.find_all('p')
        if p_text:
            text = ' '.join(map(lambda x:
                                x.text.replace('<br />','\n').strip(),
                                p_text))
        else:
            text = None
        
        return overview, text 
    
    def get_articles(self,
                     param_dict,
                     time_step = 0,
                     save_every = 0,
                     save_excel = True) -> pd.DataFrame:
        """
        Функция для скачивания статей интервалами через каждые time_step дней
        Делает сохранение таблицы через каждые save_every * time_step дней

        param_dict: dict
        ### Параметры запроса 
        ###### project - раздел поиска, например, rbcnews
        ###### category - категория поиска, например, TopRbcRu_economics
        ###### dateFrom - с даты
        ###### dateTo - по дату
        ###### query - поисковой запрос (ключевое слово), например, РБК
        ###### page - смещение поисковой выдачи (с шагом 20)
        
        ###### Deprecated:
        ###### offset - смещение поисковой выдачи
        ###### limit - лимит статей, максимум 100
        """
        param_copy = param_dict.copy()
        dateFrom = datetime.strptime(param_copy['dateFrom'], '%d.%m.%Y')
        dateTo = datetime.strptime(param_copy['dateTo'], '%d.%m.%Y')
        if dateFrom > dateTo:
            raise ValueError('dateFrom should be less than dateTo')
        
        out = pd.DataFrame()

        param_copy['page'] = '1'
        out = pd.concat([out, self._iterable_load_by_page(param_copy)], axis=0, ignore_index=True)
        
        if save_excel:
            out.to_excel("rbc_{}_{}.xlsx".format(
                param_dict['dateFrom'],
                param_dict['dateTo']))
        print('Finish')
        
        return out

    def extract_relevant_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Извлекает ключевые данные из DataFrame со статьями.
        
        Параметры:
            df: pd.DataFrame
                Исходный DataFrame, полученный из get_articles()
        
        Возвращает:
            pd.DataFrame с колонками:
            ['text', 'title', 'url', 'date', 'source']
        """
        try:
            return pd.DataFrame({
                'text': df['text'],
                'title': df['title'],
                'url': df['fronturl'],
                'date': df['publish_date_t'].apply(
                    lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y %H:%M:%S")
                ),
                'source': 'RBC'
            })
        except KeyError as e:
            print(f"Ошибка обработки данных: отсутствует колонка {e}")
            return pd.DataFrame()
            