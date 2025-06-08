from dishka import FromDishka
from fastapi import APIRouter, status
from dishka.integrations.fastapi import inject

from service import CompanyService, Agent
from service.schemas import TickerOut, AllTickersResponse, TickerCreate


ticker_router = APIRouter(prefix="/tickers", tags=["Тикеры"])


@ticker_router.get("/")
@inject
async def get_all_tickers(service: FromDishka[CompanyService]) -> AllTickersResponse:
    return await service.get_all_tickers()


@ticker_router.post("/", response_model=TickerOut, status_code=status.HTTP_201_CREATED)
@inject
async def create_ticker(ticker_data: TickerCreate, service: FromDishka[CompanyService]):
    return await service.create_ticker(ticker_data)


@ticker_router.get("/{ticker}/news_summary")
@inject
async def get_ticker_summary(ticker: str, agent: FromDishka[Agent]) -> dict:
    return {"summary": await agent.get_summary_by_ticker(ticker=ticker)}
