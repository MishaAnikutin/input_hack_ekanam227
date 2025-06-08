from qdrant_client import models
import pandas as pd
from typing import List, Dict, Any, Optional

from qdrant_client import models
import pandas as pd
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, qdrant_client, model):
        self.db = qdrant_client  
        self.model = model 

    def upload(self, df: pd.DataFrame, similarity_threshold: Optional[float] = None) -> bool:
        """
        Загрузка данных с проверкой дубликатов по одному документу.
        
        Args:
            df: DataFrame с данными для загрузки
            similarity_threshold: порог схожести для проверки дубликатов
            
        Returns:
            bool: True если загрузка прошла успешно
        """
        uploaded_count = 0
        
        # Создаем индексы для новых полей релевантности
        try:
            self.db.create_payload_index(
                collection_name="input_hak",
                field_name="probability",
                field_schema=models.PayloadSchemaType.FLOAT)
            
            # Создаем индексы для полей релевантности
            for ticker in ['relevant_for_lkoh', 'relevant_for_gazp', 'relevant_for_t', 'relevant_for_chmf']:
                self.db.create_payload_index(
                    collection_name="input_hak",
                    field_name=ticker,
                    field_schema=models.PayloadSchemaType.FLOAT)
            print("Индексы для probability и полей релевантности созданы")
        except Exception as e:
            print(f"Индексы уже существуют или ошибка: {str(e)}")
        
        for idx, doc in df.iterrows():
            if similarity_threshold is not None:
                # Проверяем на дубликаты перед загрузкой
                duplicates = self.db.search(
                    collection_name="input_hak",
                    query_vector=self.model.encode(doc["summary_text"]).tolist(),
                    limit=1,
                    score_threshold=similarity_threshold
                )
                if duplicates:
                    continue  

            # Подготавливаем payload с новыми полями
            payload = {
                "summary_text": doc["summary_text"],
                "title": doc["title"],
                "url": doc["url"],
                "date": doc["date"].isoformat() if hasattr(doc["date"], "isoformat") else doc["date"],
                "source": doc["source"],
                "market_sentiment": doc["market_sentiment"],
                "probability": doc["probability"],
                'ticker': doc['ticker'],
                'relevant_for_lkoh': doc.get('relevant_for_lkoh',np.random.rand()),  
                'relevant_for_gazp': doc.get('relevant_for_gazp', np.random.rand()),
                'relevant_for_t': doc.get('relevant_for_t', np.random.rand()),
                'relevant_for_chmf': doc.get('relevant_for_chmf', np.random.rand())
            }
            
            # Создаем точку для текущего документа
            point = models.PointStruct(
                id=idx,
                vector=self.model.encode(doc["summary_text"]).tolist(),
                payload=payload
            )
            
            # Загружаем точку сразу
            self.db.upsert(
                collection_name="input_hak",
                points=[point],
                wait=True
            )
            uploaded_count += 1
        
        print(f"Успешно загружено {uploaded_count} из {len(df)} документов")
        return True

    def search_top_k(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск с использованием стандартного search Qdrant.
        
        Возвращает список результатов в удобном формате.
        """
        results = self.db.search(
            collection_name="input_hak",
            query_vector=self.model.encode(query).tolist(),
            limit=top_k,
            with_payload=True  # Возвращаем все метаданные
        )
        
        return results
