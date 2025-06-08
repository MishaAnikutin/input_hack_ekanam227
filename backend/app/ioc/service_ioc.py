from dishka import Provider, Scope, provide

from service import UserService, CompanyService, UserTickerService
from service.agent import Agent


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    company_service = provide(UserService, provides=UserService)
    user_service = provide(CompanyService, provides=CompanyService)
    user_ticker_service = provide(
        UserTickerService, provides=UserTickerService
    )
    agent = provide(Agent, provides=Agent)
