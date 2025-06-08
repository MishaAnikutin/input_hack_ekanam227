from dishka import FromDishka
from fastapi import APIRouter, status
from dishka.integrations.fastapi import inject

from service import CompanyService
from service.schemas import TickerOut, AllTickersResponse, TickerCreate


ticker_router = APIRouter(prefix="/tickers", tags=["Тикеры"])


@ticker_router.get("/")
@inject
async def get_all_tickers(service: FromDishka[CompanyService]) -> AllTickersResponse:
    return await service.get_all_tickers()


@ticker_router.post(
    "/",
    response_model=TickerOut,
    status_code=status.HTTP_201_CREATED
)
@inject
async def create_ticker(
        ticker_data: TickerCreate,
        service: FromDishka[CompanyService]
):
    return await service.create_ticker(ticker_data)


@ticker_router.get("/tickers/{ticker}/news_summary")
async def get_ticker_summary(ticker: str) -> dict:
    summary = f'Итого по акции {ticker}:\n-Нефть упала до мирового минимума\n-Владимир путин рассказал анекдот про дачников'

    return {'summary': summary}
