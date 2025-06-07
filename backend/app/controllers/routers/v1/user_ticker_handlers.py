from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, status

from service.schemas import UserTickersResponse, AddTickerToUserRequest, UserTickerBase
from service import UserTickerService

user_ticker_router = APIRouter(prefix="/users", tags=["Пользовательские тикеры"])


@user_ticker_router.get("/{telegram_id}/tickers")
@inject
async def get_user_tickers(
        telegram_id: int,
        service: FromDishka[UserTickerService]
) -> UserTickersResponse:
    try:
        return await service.get_user_tickers(telegram_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@user_ticker_router.post(
    "/{telegram_id}/tickers",
    response_model=UserTickerBase,
    status_code=status.HTTP_201_CREATED
)
@inject
async def add_ticker_to_user(
        request: AddTickerToUserRequest,
        service: FromDishka[UserTickerService]
) -> UserTickerBase:
    try:
        return await service.add_ticker_to_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e))
