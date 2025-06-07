import datetime
from io import BytesIO

import httpx
from config import Config


async def get_all_tickers():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{Config.API_URL}/tickers/")

        return response.json()


async def get_or_create_user(user_id: int, username: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{Config.API_URL}/users/",
            json={"telegram_id": user_id, "username": username}
        )

        return response.json()


async def add_ticker_to_user(user_id: int, ticker: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{Config.API_URL}/users/{user_id}/tickers",
            json={"ticker_symbol": ticker, "telegram_id": user_id}
        )

        return response.status_code < 400


async def delete_ticker_from_user(user_id: int, ticker: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{Config.API_URL}/users/{user_id}/tickers/{ticker}"
        )

        return response.status_code < 400


async def get_user_tickers(telegram_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{Config.API_URL}/users/{telegram_id}/tickers")

        return response.json().get("tickers", [])


import apimoex
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import BytesIO
import datetime


class Stock:
    def __init__(self, ticker: str):
        self._ticker = ticker
        self._session = requests.Session()

    def _get_data(self):
        start = datetime.date.today() - datetime.timedelta(days=1)
        print(f'{start = }')

        data = apimoex.get_board_candles(self._session, security=self._ticker, interval=1, start=start)
        df = pd.DataFrame(data)
        print(df.columns)
        df['begin'] = pd.to_datetime(df['begin'])
        return df

    def build_plot(self, sentiment_data: pd.DataFrame) -> bytes:
        data = self._get_data()

        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax2 = ax.twinx()  # Создаем вторую ось Y

        # Убираем верхнюю и правую границы для обеих осей
        ax.spines[['top', 'right']].set_visible(False)
        ax2.spines[['top', 'right']].set_visible(False)

        # График цены (основная ось)
        ax.plot(
            data['begin'],  # Исправлено: 'TRADEDATE'
            data['open'],
            color='black',
            linewidth=2,
            label='Цена открытия'
        )

        # # График сентимента (вторая ось)
        # ax2.plot(
        #     sentiment_data['date'],
        #     sentiment_data['sentiment_value'],
        #     color='blue',
        #     linestyle='--',
        #     linewidth=2,
        #     label='Новостной индекс'
        # )

        # Настройка оформления
        ax.set_title(f'Динамика цен и сентимента: {self._ticker}', fontsize=14)
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_ylabel('Цена открытия', color='black', fontsize=10)
        ax2.set_ylabel('Новостной индекс', color='blue', fontsize=10)

        # Цвет подписей значений осей
        ax.tick_params(axis='y', labelcolor='black')
        ax2.tick_params(axis='y', labelcolor='blue')

        # Сетка и расположение легенд
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.yaxis.set_major_locator(ticker.LinearLocator(10))  # Деления на оси Y

        # Объединение легенд
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='best')

        # Поворот дат и компактное размещение
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Сохранение в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=120)
        buf.seek(0)
        plt.close(fig)

        return buf.getvalue()
