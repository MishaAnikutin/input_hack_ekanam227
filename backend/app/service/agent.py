from openai import OpenAI
from qdrant_client import AsyncQdrantClient, models

from service.schemas import (
    Resonance,
    Interpretation,
    Resonances,
    WeeklySummarizeResponse,
)

from typing import List
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range
from datetime import datetime, timedelta
import re

from typing import List
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range
from datetime import datetime, timedelta
import re


class Agent:
    def __init__(self, vector_client: AsyncQdrantClient, llm_client: OpenAI):
        self._vector_client = vector_client
        self._llm_client = llm_client

    async def get_summary_by_ticker(self, ticker: str) -> str:
        # ticker_filter = Filter(
        #     must=[FieldCondition(key=f"relevant_for_{ticker.lower()}", match=Range(gte=0.8))]
        # )

        records = await self._vector_client.scroll(
            collection_name="input_hak",
            # scroll_filter=ticker_filter,
            limit=100,
            with_payload=True
        )

        print(records)
        documents = [rec.payload.get("summary_text") or rec.payload.get("title", "") for rec in records[0]]
        context = "\n".join(documents)[:12000]  # Ограничиваем длину контекста

        # Генерируем суммаризацию с помощью LLM
        response = self._llm_client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": "Ты финансовый аналитик. Создай очень краткую сводку по новостям, максимум 5 предложений. Структурируй свой ответ по пунктам, каждый пункт - 2-3 предложения"},
                {"role": "user", "content": f"Сгенерируй краткую сводку по {ticker} на основе данных:\n{context}"}
            ]
        )

        return f"Итого по акции {ticker}:\n{response.choices[0].message.content}"

    async def get_ticker_most_resonance(
            self, ticker: str, limit: int = 5
    ) -> Resonances:
        # Формируем фильтр и сортировку
        relevance_field = f"relevant_for_{ticker.lower()}"
        # ticker_filter = Filter(
        #     must=[
        #         FieldCondition(key=relevance_field, range=Range(gte=0.5))
        #     ]
        # )

        # Получаем отсортированные результаты
        records = await self._vector_client.scroll(
            collection_name="input_hak",
            # query_filter=ticker_filter,
            limit=limit,
            # order_by=relevance_field,
            order_by='probability'
        )

        # Формируем список резонансов
        resonances = []

        for rec in records[0]:
            payload = rec.payload

            market_sentiment = float(payload.get("market_sentiment", 0))
            proba = float(payload.get("probability", 0))
            resonances.append(
                Resonance(
                    text=payload.get("title", ""),
                    sentiment=market_sentiment * proba,
                    search_index=payload.get(relevance_field, 0.0),
                    source=payload.get("source", ""),
                    url=payload.get("url", "")
                )
            )

        return Resonances(resonances=resonances)

    async def get_an_interpretation(
            self,
            summary: str,
            resonance: str,
    ) -> Interpretation:
        # Генерируем интерпретацию с помощью LLM
        response = self._llm_client.chat.completions.create(
            model="deepseek-r1",
            messages=[
                {"role": "system", "content": "Ты старший аналитик фондового рынка. Проанализируй сводку и новость."},
                {"role": "user", "content":
                    f"Сводка: {summary}\n\nКлючевая новость: {resonance}\n\n"
                    "Дай анализ в формате:\n"
                    "think: <аналитическое мнение>\n"
                    "answer: <финальный вывод>"
                 }
            ]
        )

        # Парсим ответ LLM
        content = response.choices[0].message.content
        think_match = re.search(r"think:\s*(.+)", content, re.DOTALL)
        answer_match = re.search(r"answer:\s*(.+)", content, re.DOTALL)

        return Interpretation(
            think=think_match.group(1).strip() if think_match else "Анализ не доступен",
            answer=answer_match.group(1).strip() if answer_match else "Вывод не доступен"
        )

    async def get_weekly_summary_and_interpretation(self) -> WeeklySummarizeResponse:
        # Рассчитываем даты
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        week_end = today.strftime("%Y-%m-%d")

        # # Фильтр по дате
        # date_filter = Filter(
        #     must=[FieldCondition(key="date", range=Range(gte=week_start, lte=week_end))]
        # )

        # Получаем документы за неделю
        records = await self._vector_client.scroll(
            collection_name="input_hak",
            # scroll_filter=date_filter,
            limit=10,
            with_payload=True
        )

        # Формируем контекст
        context = "\n".join(
            f"[{rec.payload.get('date')}] {rec.payload.get('title')}"
            for rec in records
        )[:15000]

        # Генерируем недельную сводку
        summary_response = self._llm_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ты главный экономист. Создай недельный обзор рынка."},
                {"role": "user", "content": f"Создай краткий обзор за период {week_start}-{week_end}:\n{context}"}
            ]
        )
        summary = summary_response.choices[0].message.content

        # Генерируем интерпретацию
        interpretation = await self.get_an_interpretation(
            summary=summary,
            resonance="Недельный рыночный отчет"
        )

        return WeeklySummarizeResponse(
            summary=summary,
            interpretation=interpretation
        )
