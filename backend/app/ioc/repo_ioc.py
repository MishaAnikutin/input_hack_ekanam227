from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide

from config import Config
from database.clients import SQLiteAsyncSession
from qdrant_client import AsyncQdrantClient
from openai import OpenAI

from database.clients.sqlite import get_async_session
from repos import CompanyRepository, UserRepository, UserTickerRepository


class RepoProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    async def client_sql(self) -> AsyncIterable[SQLiteAsyncSession]:
        async with get_async_session() as session:
            yield session

    @provide(scope=Scope.APP)
    async def client_vector(self) -> AsyncQdrantClient:
        return AsyncQdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_KEY)

    @provide(scope=Scope.APP)
    async def client_llm(self) -> OpenAI:
        return OpenAI(base_url=Config.OPENAI_URL, api_key=Config.OPENAI_KEY)

    company_repository = provide(CompanyRepository, provides=CompanyRepository)
    user_repository = provide(UserRepository, provides=UserRepository)
    user_ticker_repository = provide(
        UserTickerRepository, provides=UserTickerRepository
    )
