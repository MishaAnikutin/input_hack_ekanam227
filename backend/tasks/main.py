import requests
from bs4 import BeautifulSoup
import sqlite3
import schedule
import time
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import joblib  # Для загрузки ML-модели

# Конфигурация
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
NEWS_SOURCES = [
    "https://example.com/news/rss",
    "https://anotherexample.org/feed"
]
DB_NAME = "news_bot.db"
CHECK_INTERVAL = 5  # минут

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)



# Работа с базой данных
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (chat_id INTEGER PRIMARY KEY, username TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_news
                 (news_id TEXT PRIMARY KEY)''')  # Для предотвращения дубликатов
    conn.commit()
    conn.close()


def add_user(chat_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (chat_id, username))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


def mark_as_sent(news_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO sent_news VALUES (?)", (news_id,))
    conn.commit()
    conn.close()


def is_already_sent(news_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM sent_news WHERE news_id=?", (news_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


# Парсер новостей
def parse_news(source):
    try:
        response = requests.get(source, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        news_items = []

        for item in soup.find_all('item'):
            title = item.title.text.strip()
            link = item.link.text.strip()
            description = item.description.text.strip() if item.description else ""

            # Генерируем уникальный ID
            news_id = f"{source}-{hash(link)}"

            news_items.append({
                'id': news_id,
                'title': title,
                'text': f"{title}\n{description}",
                'link': link
            })
        return news_items
    except Exception as e:
        logger.error(f"Ошибка парсинга {source}: {str(e)}")
        return []


# Обработчик команд бота
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.username)
    update.message.reply_text(f"Привет {user.first_name}! Теперь ты будешь получать важные новости.")


# Рассылка новостей
def send_news_to_users(news_item):
    bot = Bot(token=TOKEN)
    users = get_all_users()
    message = f"🚨 Важная новость! 🚨\n\n{news_item['title']}\n\n{news_item['link']}"

    for chat_id in users:
        try:
            bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Отправлено пользователю {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки для {chat_id}: {str(e)}")


# Основная задача для планировщика
def monitoring_task():
    logger.info("Запуск проверки новостей...")
    model = NewsScoringModel()

    for source in NEWS_SOURCES:
        news_items = parse_news(source)
        logger.info(f"Найдено {len(news_items)} новостей в {source}")

        for item in news_items:
            if is_already_sent(item['id']):
                continue

            score = model.predict(item['text'])
            if score > 0.05:
                logger.info(f"Важная новость! Скор: {score:.4f} - {item['title']}")
                send_news_to_users(item)
                mark_as_sent(item['id'])


# Инициализация
def main():
    init_db()

    # Запуск бота
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()

    # Настройка планировщика
    schedule.every(CHECK_INTERVAL).minutes.do(monitoring_task)
    logger.info(f"Сервис запущен. Проверка каждые {CHECK_INTERVAL} минут.")

    # Основной цикл
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()