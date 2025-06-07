from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from database.clients import SQLiteAsyncSession

from database.clients.sqlite import get_async_session
from repos import CompanyRepository, UserRepository, UserTickerRepository


class RepoProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    async def client(self) -> AsyncIterable[SQLiteAsyncSession]:
        async with get_async_session() as session:
            yield session

    company_repository = provide(CompanyRepository, provides=CompanyRepository)
    user_repository = provide(UserRepository, provides=UserRepository)
    user_ticker_repository = provide(
        UserTickerRepository, provides=UserTickerRepository
    )
