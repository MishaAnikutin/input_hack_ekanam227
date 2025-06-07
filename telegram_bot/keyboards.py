from aiogram.types import ReplyKeyboardMarkup


buttons = [
    ["Подписаться на рассылку (/broadcast)"],
    ["Суммаризация новостей (/summary)"],
    ["Аналитика по тикеру (/ticker)"]
]
start_keyboard = ReplyKeyboardMarkup(
    keyboard=buttons,
    resize_keyboard=True
)


async def get_ticker_buttons(dialog_manager):
    tickers = dialog_manager.current_context().dialog_data["tickers"]
    # Логика формирования кнопок для пагинации
    return {"tickers": tickers}
