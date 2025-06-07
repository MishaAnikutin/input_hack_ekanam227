from dishka import make_async_container

from .repo_ioc import RepoProvider
from .service_ioc import ServiceProvider


container = make_async_container(RepoProvider(), ServiceProvider())


__all__ = ('container', )
