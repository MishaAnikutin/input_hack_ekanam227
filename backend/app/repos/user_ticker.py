from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserTickerAssociation, UserModel, CompanyModel


class UserTickerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticker_to_user(
        self, user_id: int, ticker_id: int
    ) -> UserTickerAssociation:
        # Проверка существования связи
        existing = await self.session.execute(
            select(UserTickerAssociation).where(
                UserTickerAssociation.user_id == user_id,
                UserTickerAssociation.ticker_id == ticker_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Тикер уже в корзине пользователя")

        # Создание новой ассоциации
        new_association = UserTickerAssociation(user_id=user_id, ticker_id=ticker_id)
        self.session.add(new_association)
        await self.session.commit()
        return new_association

    async def remove_ticker_from_user(self, user_id: int, ticker_id: int) -> bool:
        result = await self.session.execute(
            delete(UserTickerAssociation)
            .where(
                UserTickerAssociation.user_id == user_id,
                UserTickerAssociation.ticker_id == ticker_id,
            )
            .returning(UserTickerAssociation)
        )
        if not result.scalar_one_or_none():
            return False
        await self.session.commit()
        return True

    async def get_user_tickers(self, user_id: int) -> list[CompanyModel]:
        result = await self.session.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.ticker_associations).selectinload(
                    UserTickerAssociation.company
                )
            )
            .where(UserModel.id == user_id)
        )
        user = result.scalar_one()
        return [assoc.company for assoc in user.ticker_associations]

    async def get_ticker_subscribers(self, ticker_id: int) -> list[UserModel]:
        result = await self.session.execute(
            select(CompanyModel)
            .options(
                selectinload(CompanyModel.user_associations).selectinload(
                    UserTickerAssociation.user
                )
            )
            .where(CompanyModel.id == ticker_id)
        )
        company = result.scalar_one()
        return [assoc.user for assoc in company.user_associations]

    async def user_has_ticker(self, user_id: int, ticker_id: int) -> bool:
        result = await self.session.execute(
            select(UserTickerAssociation).where(
                UserTickerAssociation.user_id == user_id,
                UserTickerAssociation.ticker_id == ticker_id,
            )
        )
        return result.scalar_one_or_none() is not None
