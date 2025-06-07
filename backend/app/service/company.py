from repos import CompanyRepository
from service.schemas import (
    TickerWithUsers,
    TickerOut,
    UserOut,
    AllTickersResponse,
    SearchTickersResponse,
    TickerCreate,
)


class CompanyService:
    def __init__(self, repo: CompanyRepository):
        self.repo = repo

    async def create_ticker(self, ticker_data: TickerCreate) -> TickerOut:
        """Создает новый тикер"""
        ticker = await self.repo.create_ticker(
            ticker=ticker_data.ticker, name=ticker_data.name
        )
        return TickerOut.from_orm(ticker)

    async def get_all_tickers(self) -> AllTickersResponse:
        """Получает все тикеры"""
        tickers = await self.repo.get_all_tickers()
        return AllTickersResponse(
            count=len(tickers), tickers=[TickerOut.from_orm(t) for t in tickers]
        )

    async def search_tickers(self, query: str) -> SearchTickersResponse:
        """Ищет тикеры по запросу"""
        tickers = await self.repo.search_tickers(query)
        return SearchTickersResponse(results=[TickerOut.from_orm(t) for t in tickers])

    async def get_ticker_by_symbol(self, symbol: str) -> TickerOut:
        """Получает тикер по символу"""
        ticker = await self.repo.get_ticker_by_symbol(symbol)
        if not ticker:
            raise ValueError("Тикер не найден")
        return TickerOut.from_orm(ticker)

    async def get_ticker_with_users(self, symbol: str) -> TickerWithUsers:
        """Получает тикер с подписанными пользователями"""
        ticker = await self.repo.get_ticker_by_symbol(symbol)
        if not ticker:
            raise ValueError("Тикер не найден")

        return TickerWithUsers(
            **TickerOut.from_orm(ticker).dict(),
            users=[UserOut.from_orm(u) for u in ticker.users]
        )
