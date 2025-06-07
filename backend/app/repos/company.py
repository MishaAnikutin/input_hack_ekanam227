from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import CompanyModel


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ticker(self, ticker: str, name: str) -> CompanyModel:
        # Проверяем существование тикера
        existing = await self.get_ticker_by_symbol(ticker)
        if existing:
            raise ValueError(f"Тикер {ticker} уже существует")

        new_company = CompanyModel(ticker=ticker, name=name)
        self.session.add(new_company)
        await self.session.commit()
        await self.session.refresh(new_company)
        return new_company

    async def update_ticker(
        self, ticker_id: int, new_ticker: str, new_name: str
    ) -> CompanyModel:
        company = await self.session.get(CompanyModel, ticker_id)
        if not company:
            raise ValueError("Тикер не найден")

        # Проверяем конфликты имен
        if new_ticker != company.ticker:
            existing = await self.get_ticker_by_symbol(new_ticker)
            if existing:
                raise ValueError(f"Тикер {new_ticker} уже существует")

        company.ticker = new_ticker
        company.name = new_name
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def delete_ticker(self, ticker_id: int):
        company = await self.session.get(CompanyModel, ticker_id)
        if not company:
            raise ValueError("Тикер не найден")

        await self.session.delete(company)
        await self.session.commit()

    async def get_ticker_by_id(self, ticker_id: int) -> CompanyModel:
        return await self.session.get(CompanyModel, ticker_id)

    async def get_ticker_by_symbol(self, symbol: str) -> CompanyModel:
        result = await self.session.execute(
            select(CompanyModel).where(
                func.lower(CompanyModel.ticker) == func.lower(symbol)
            )
        )
        return result.scalar_one_or_none()

    async def get_all_tickers(self) -> list[CompanyModel]:
        result = await self.session.execute(select(CompanyModel))
        return result.scalars().all()

    async def search_tickers(self, query: str) -> list[CompanyModel]:
        """Поиск тикеров по символу или названию компании"""
        query = query.lower()
        result = await self.session.execute(
            select(CompanyModel)
            .where(
                func.lower(CompanyModel.ticker).contains(query)
                | func.lower(CompanyModel.name).contains(query)
            )
            .limit(10)
        )
        return result.scalars().all()
