import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import ParseMode

from bot.config import BOT_TOKEN
from bot.database.db import db

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# Импорт и регистрация хендлеров
from bot.handlers.start import router as start_router
from bot.handlers.purchase import router as purchase_router  
from bot.handlers.support import router as support_router


async def on_startup(_):
    await db.init()
    logging.info("Bot started!")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
