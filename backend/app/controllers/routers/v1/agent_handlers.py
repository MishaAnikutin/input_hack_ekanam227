from dishka import FromDishka
from fastapi import APIRouter, status
from dishka.integrations.fastapi import inject

from service.agent import Agent
from service.schemas import (
    Resonance,
    Interpretation,
    Resonances,
    WeeklySummarizeResponse,
)

agent_router = APIRouter(prefix="/agent", tags=["Агент"])


@agent_router.get("/{ticker}/most_resonance/limit/{limit}")
@inject
async def get_ticker_most_resonance(
    agent_service: FromDishka[Agent], ticker: str, limit: int = 5
) -> Resonances:
    return await agent_service.get_ticker_most_resonance(ticker=ticker, limit=limit)


@agent_router.post("/interpretation")
@inject
async def get_an_interpretation(
    summary: str, resonance: str, agent: FromDishka[Agent]
) -> Interpretation:
    interpretation = await agent.get_an_interpretation(summary, resonance)
    return {"interpretation": interpretation}


@agent_router.get(f"/weekly_summary_and_interpretation")
@inject
async def get_weekly_summary_and_interpretation(
    agent: FromDishka[Agent],
) -> WeeklySummarizeResponse:
    return await agent.get_weekly_summary_and_interpretation()
