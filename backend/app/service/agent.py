from openai import OpenAI
from qdrant_client import AsyncQdrantClient, models

from service.schemas import (
    Resonance,
    Interpretation,
    Resonances,
    WeeklySummarizeResponse,
)


class Agent:
    def __init__(self, vector_client: AsyncQdrantClient, llm_client: OpenAI):
        self._vector_client = vector_client
        self._llm_client = llm_client

    async def get_summary_by_ticker(self, ticker: str) -> str:
        return f"Итого по акции {ticker}:\n-Нефть упала до мирового минимума\n-Владимир путин рассказал анекдот про дачников"

    async def get_ticker_most_resonance(
        self, ticker: str, limit: int = 5
    ) -> Resonances:
        return Resonances(
            resonances=[
                Resonance(text='нефть рухнула!!!', sentiment=-1, search_index=999.0, source='ТАСС',
                          url='http://vk.com/'),
                Resonance(text='путин пошутил, всем смеятсья!!!', sentiment=0.99, search_index=228.0,
                          source='Интерфакс',
                          url='http://vk.com/')
            ])

    async def get_an_interpretation(
        self,
        summary: str,
        resonance: str,
    ) -> Interpretation:
        return Interpretation(
            think="блин что вообще происходит ...",
            answer="Интерпретация: Все плохо, одному путину смешно ...",
        )

    async def get_weekly_summary_and_interpretation(self) -> WeeklySummarizeResponse:
        return WeeklySummarizeResponse(
            summary="Все хорошо!",
            interpretation=Interpretation(
                think="блин что вообще происходит ...",
                answer="Интерпретация: Все плохо, одному путину смешно ...",
            ),
        )
