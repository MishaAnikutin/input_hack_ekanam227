from dishka import FromDishka
from dishka.integrations.fastapi import inject

from service import UserService
from service.schemas import UserOut, UserCreate
from fastapi import APIRouter, HTTPException, status

user_router = APIRouter(prefix="/users", tags=["Пользователи"])


@user_router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Создать или получить пользователя",
)
@inject
async def get_or_create_user_handler(
    user_data: UserCreate, service: FromDishka[UserService]
):
    try:
        return await service.get_or_create_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
