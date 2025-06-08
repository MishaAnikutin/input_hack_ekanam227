from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from ioc import container
from config import Config
from controllers import router
from database.clients.sqlite import init_db


app = FastAPI(
    title="economics-news-system", docs_url="/docs", openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWS_ORIGINS.split(),
    allow_credentials=True,
    allow_methods=Config.ALLOWS_ORIGINS.split(),
    allow_headers=Config.ALLOWS_ORIGINS.split(),
)

app.include_router(router)
setup_dishka(container, app)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def health_check():
    return {"status": "ok"}
