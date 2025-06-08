from openai import OpenAI
from qdrant_client import AsyncQdrantClient,models

from service.schemas import Resonance, Interpretation, Resonances, WeeklySummarizeResponse


class Agent:
    def __init__(self, vector_client: AsyncQdrantClient, llm_client: OpenAI):
        self._vector_client = vector_client
        self._llm_client = llm_client

    async def get_summary_by_ticker(self, ticker: str) -> str:
        return f'Итого по акции {ticker}:\n-Нефть упала до мирового минимума\n-Владимир путин рассказал анекдот про дачников'

async def get_ticker_most_resonance(self, ticker: str, limit: int = 5) -> Resonances:
    # Получаем записи с наивысшим probability (DESC - по убыванию)
    top_k_points_best = self.vector_client.scroll(
        collection_name="input_hak",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="probability",
                    range=models.Range(gte=-1)
                )
        ],
        limit=limit,
        order_by=models.OrderBy(
            key="probability",
            direction=models.Direction.DESC  # Сортировка по убыванию
        ),
        with_payload=True,
    ))

    # Получаем записи с наименьшим probability (ASC - по возрастанию)
    top_k_points_worst = self.vector_client.scroll(
        collection_name="input_hak",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="probability",
                    range=models.Range(gte=-1)
                )
        ],
        limit=limit,
        order_by=models.OrderBy(
            key="probability",
            direction=models.Direction.ASC  # Сортировка по возрастанию
        ),
        with_payload=True,
    )
    )

    # Создаем объекты Resonance
    best_resonances = [
        Resonance(
            text=point.payload['summary_text'],
            sentiment=point.payload['probability'],
            source=point.payload.get('source', 'Unknown'),
            url=point.payload['url']
        )
        for point in top_k_points_best[0]
    ]

    worst_resonances = [
        Resonance(
            text=point.payload['summary_text'],
            sentiment=point.payload['probability'],
            source=point.payload.get('source', 'Unknown'),
            url=point.payload['url']
        )
        for point in top_k_points_worst[0]
    ]

    return [best_resonances, worst_resonances]


    async def get_an_interpretation(self, summary: str, resonance: str,) -> Interpretation:
        return Interpretation(think="блин что вообще происходит ...",
                              answer='Интерпретация: Все плохо, одному путину смешно ...')

    async def get_weekly_summary_and_interpretation(self) -> WeeklySummarizeResponse:
        return WeeklySummarizeResponse(
            summary='Все хорошо!',
            interpretation=Interpretation(
                think="блин что вообще происходит ...",
                answer='Интерпретация: Все плохо, одному путину смешно ...'
            )
        )
