from fastapi import APIRouter

from .ticker_handlers import ticker_router
from .user_handlers import user_router
from .user_ticker_handlers import user_ticker_router
from .agent_handlers import agent_router

router_v1 = APIRouter(prefix="/v1")

router_v1.include_router(ticker_router)
router_v1.include_router(user_router)
router_v1.include_router(user_ticker_router)
router_v1.include_router(agent_router)
