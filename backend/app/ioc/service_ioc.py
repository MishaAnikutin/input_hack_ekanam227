from dishka import Provider, Scope, provide

from service import UserService, CompanyService, UserTickerService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    company_service = provide(UserService, provides=UserService)
    user_service = provide(CompanyService, provides=CompanyService)
    user_ticker_service = provide(
        UserTickerService, provides=UserTickerService
    )
