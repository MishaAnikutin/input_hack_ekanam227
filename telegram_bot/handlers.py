import pandas as pd
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from services import (
    get_all_tickers,
    get_or_create_user,
    add_ticker_to_user,
    delete_ticker_from_user,
    get_user_tickers, Stock, get_ticker_summary, get_ticker_most_resonance, get_an_interpretation,
    get_weekly_summary_and_interpretation
)

router = Router()

# Общие текстовые константы
WELCOME_TEXT = (
    "👋 Добрый день, {username}!\n\n"
    "📊 Я бот для отслеживания финансовых новостей. Вот что я умею:\n\n"
    "• /broadcast - Управление подписками на акции\n"
    "• /summary - Суммаризация новостей за неделю\n"
    "• /ticker - Аналитика по конкретному тикеру\n\n"
    "Начните с управления подписками, чтобы получать персонализированные новости!"
)

SUBSCRIPTION_MANAGEMENT_TEXT = "📊 Выберите акции для подписки:"
CLOSE_TEXT = "🔒 Закрыть"
SUBSCRIPTION_ERROR = "⚠️ Ошибка подписки!"
UNSUBSCRIPTION_ERROR = "⚠️ Ошибка отписки!"


@router.message(Command("start"))
async def start_command(message: Message):
    user = message.from_user
    await get_or_create_user(user.id, user.username or "пользователь")
    await message.answer(WELCOME_TEXT.format(username=user.username or "пользователь"))


async def build_subscription_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Строит инлайн-клавиатуру для управления подписками"""
    builder = InlineKeyboardBuilder()

    try:
        # Получаем данные из API
        all_tickers = [t["ticker"] for t in (await get_all_tickers())["tickers"]]
        all_user_tickers = await get_user_tickers(user_id)
        user_tickers = [el['ticker'] for el in all_user_tickers]
        print(f'\t{user_tickers = }')
        # Создаем кнопки для тикеров
        for ticker in all_tickers:
            is_subscribed = ticker in user_tickers
            button_text = f"✅ {ticker}" if is_subscribed else ticker
            action = "unsubscribe" if is_subscribed else "subscribe"
            builder.button(text=button_text, callback_data=f"{action}:{ticker}")

    except Exception as e:
        print(f"Ошибка при построении клавиатуры: {e}")
        builder.button(text="Ошибка загрузки данных", callback_data="error")

    # Добавляем кнопку закрытия
    builder.button(text=CLOSE_TEXT, callback_data="close")
    builder.adjust(2, repeat=True)
    return builder.as_markup()


@router.message(Command("broadcast"))
async def manage_subscriptions(message: Message):
    user = message.from_user
    await get_or_create_user(user.id, user.username or "")

    try:
        keyboard = await build_subscription_keyboard(user.id)
        await message.answer(SUBSCRIPTION_MANAGEMENT_TEXT, reply_markup=keyboard)
    except Exception as e:
        print(f"Ошибка управления подписками: {e}")
        await message.answer("🚫 Произошла ошибка при загрузке данных")


async def update_subscription_message(callback: CallbackQuery):
    """Обновляет сообщение с клавиатурой подписок"""
    try:
        keyboard = await build_subscription_keyboard(callback.from_user.id)
        await callback.message.edit_text(
            text=SUBSCRIPTION_MANAGEMENT_TEXT,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка обновления клавиатуры: {e}")
        await callback.answer("🚫 Ошибка обновления", show_alert=True)
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("subscribe:"))
async def subscribe_ticker(callback: CallbackQuery):
    ticker = callback.data.split(":", 1)[1]
    if await add_ticker_to_user(callback.from_user.id, ticker):
        await update_subscription_message(callback)
    else:
        await callback.answer(SUBSCRIPTION_ERROR, show_alert=True)


@router.callback_query(F.data.startswith("unsubscribe:"))
async def unsubscribe_ticker(callback: CallbackQuery):
    ticker = callback.data.split(":", 1)[1]
    if await delete_ticker_from_user(callback.from_user.id, ticker):
        await update_subscription_message(callback)
    else:
        await callback.answer(UNSUBSCRIPTION_ERROR, show_alert=True)


@router.callback_query(F.data == "close")
async def close_subscriptions(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Настройки подписок закрыты")


# Обработчики других команд


@router.message(Command("ticker"))
async def ticker_command(message: Message):
    all_tickers = [t["ticker"] for t in (await get_all_tickers())["tickers"]]
    builder = InlineKeyboardBuilder()
    for ticker in all_tickers:
        builder.button(text=ticker, callback_data=f'ticker_analytics:{ticker}')
    builder.adjust(2)

    await message.answer("🔍 Введите тикер для получения аналитики:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('ticker_analytics'))
async def ticker_analytics(callback: CallbackQuery):
    ticker = callback.data.split(':', maxsplit=1)[1]

    stock = Stock(ticker)

    msg = await callback.message.answer(text='Генерируем график...')
    plot_bytes = stock.build_plot(sentiment_data=pd.DataFrame({'date': [], 'sentiment_value': []}))
    await msg.delete()
    photo = BufferedInputFile(plot_bytes, filename=f"{ticker}_chart.png")
    caption = f'Аналитика акции {ticker}'
    await callback.message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode=ParseMode.HTML,
    )

    msg = await callback.message.answer(text='Суммаризируем новости...')
    ticker_summary = await get_ticker_summary(ticker=ticker)
    await callback.message.answer(text=f'Саммари:\n\n{ticker_summary}')
    await msg.delete()

    msg = await callback.message.answer(text='Находим самые резонансные новости...')
    ticker_most_resonance = await get_ticker_most_resonance(ticker=ticker, limit=5)

    resonanse_text = 'Топ новостей по сентименту и поисковым запросам:\n\n'
    for i, resonanse in enumerate(ticker_most_resonance):
        resonanse_text += (f'{i + 1}) {resonanse.source.upper()}\n\t{resonanse.text[:100]}... ({resonanse.url})'
                           f'\n\tСентимент: {resonanse.sentiment:0.1f}, '
                           f'\n\tПоисковая частота: {resonanse.search_index:0.1f}\n\n')

    await callback.message.answer(text=resonanse_text)
    await msg.delete()
    msg = await callback.message.answer(text='Интерпретируем...')
    interpretation = await get_an_interpretation(summary=ticker_summary, resonance=resonanse_text)
    await msg.delete()
    await callback.message.answer(text=f'Размышления: {interpretation.think}\n\nИтог: {interpretation.answer}')


@router.message(Command("summary"))
async def summary_command(message: Message):
    await message.answer("📈 Суммаризация новостей за неделю:")
    summary, interpretation = await get_weekly_summary_and_interpretation()

    await message.answer(text=f'Саммари: {summary}')
    await message.answer(text=f'Интерпретация:\nРазмышления: {interpretation.think}\n\nИтог: {interpretation.answer}')

