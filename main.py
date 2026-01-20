import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 3000))

# Инициализация бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# === HTTP Сервер для MiniApp ===
async def handle_index(request):
    return web.FileResponse('./web/index.html')

async def handle_privacy(request):
    return web.FileResponse('./web/privacy.html')

async def handle_terms(request):
    return web.FileResponse('./web/terms.html')

async def handle_health(request):
    return web.json_response({"status": "ok", "bot": "running"})


def create_app():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/privacy', handle_privacy)
    app.router.add_get('/terms', handle_terms)
    app.router.add_get('/health', handle_health)
    app.router.add_static('/css/', path='./web/css/', name='css')
    app.router.add_static('/js/', path='./web/js/', name='js')
    return app


# === Telegram Bot Handlers ===
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Тексты
WELCOME_TEXT = """
🌟 <b>Добро пожаловать в магазин Telegram Stars!</b>

Здесь вы можете быстро и безопасно приобрести звёзды Telegram.

⭐ <b>Почему выбирают нас:</b>
• Моментальная доставка
• Выгодные бонусы
• Безопасные платежи
• Поддержка 24/7

Выберите действие ниже 👇
"""

PRIVACY_TEXT = """
📜 <b>Политика конфиденциальности</b>

<b>1. Сбор данных</b>
Мы собираем только необходимые данные:
• Telegram ID пользователя
• Username (при наличии)
• История покупок

<b>2. Использование данных</b>
Данные используются исключительно для:
• Обработки заказов
• Поддержки пользователей
• Улучшения сервиса

<b>3. Защита данных</b>
• Мы не передаём данные третьим лицам
• Все данные хранятся в зашифрованном виде

<b>4. Удаление данных</b>
Вы можете запросить удаление ваших данных, обратившись в поддержку.
"""

TERMS_TEXT = """
📋 <b>Пользовательское соглашение</b>

<b>1. Общие положения</b>
Используя данный сервис, вы соглашаетесь с условиями ниже.

<b>2. Услуги</b>
• Мы предоставляем услуги по продаже Telegram Stars
• Доставка осуществляется автоматически после оплаты

<b>3. Оплата</b>
• Оплата производится через Telegram Payments
• Все платежи являются окончательными

<b>4. Ограничения</b>
• Запрещено использовать бота для мошенничества
• Нарушители блокируются без возврата средств
"""

SUPPORT_TEXT = """
💬 <b>Служба поддержки</b>

Если у вас возникли вопросы или проблемы:

📩 Напишите нам: @your_support
⏰ Время ответа: до 1 часа

Мы всегда рады помочь!
"""

PACKAGES_TEXT = """
🛒 <b>Выберите пакет звёзд:</b>

Чем больше пакет — тем больше бонусных звёзд!
"""

# Пакеты
STAR_PACKAGES = [
    {"id": 1, "stars": 50, "price": 50, "bonus": 0},
    {"id": 2, "stars": 100, "price": 100, "bonus": 5},
    {"id": 3, "stars": 250, "price": 250, "bonus": 15},
    {"id": 4, "stars": 500, "price": 500, "bonus": 50},
    {"id": 5, "stars": 1000, "price": 1000, "bonus": 150},
]


# Клавиатуры
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(
        text="🛒 Купить звёзды",
        callback_data="buy_stars"
    ))
    
    builder.row(InlineKeyboardButton(
        text="📦 Мои покупки",
        callback_data="my_purchases"
    ), InlineKeyboardButton(
        text="💬 Поддержка",
        callback_data="support"
    ))
    
    builder.row(InlineKeyboardButton(
        text="📜 Политика конфиденциальности",
        callback_data="privacy"
    ))
    
    builder.row(InlineKeyboardButton(
        text="📋 Пользовательское соглашение",
        callback_data="terms"
    ))
    
    return builder.as_markup()


def get_packages_keyboard():
    builder = InlineKeyboardBuilder()
    
    for pkg in STAR_PACKAGES:
        bonus_text = f" +{pkg['bonus']}🎁" if pkg['bonus'] > 0 else ""
        builder.row(InlineKeyboardButton(
            text=f"⭐ {pkg['stars']}{bonus_text} — {pkg['price']} Stars",
            callback_data=f"package_{pkg['id']}"
        ))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()


def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_main"))
    return builder.as_markup()


# Хендлеры
@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"User {message.from_user.id} started bot")
    await message.answer(WELCOME_TEXT, reply_markup=get_main_keyboard())


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "buy_stars")
async def show_packages(callback: CallbackQuery):
    await callback.message.edit_text(PACKAGES_TEXT, reply_markup=get_packages_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("package_"))
async def select_package(callback: CallbackQuery):
    package_id = int(callback.data.split("_")[1])
    pkg = next((p for p in STAR_PACKAGES if p["id"] == package_id), None)
    
    if pkg:
        bonus_text = f" + {pkg['bonus']} бонусных" if pkg['bonus'] > 0 else ""
        text = f"""
⭐ <b>Вы выбрали пакет:</b>

📦 Звёзд: <b>{pkg['stars']}{bonus_text}</b>
💰 Цена: <b>{pkg['price']} Stars</b>

Для оплаты нажмите кнопку ниже.
"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text=f"💳 Оплатить {pkg['price']} ⭐",
            callback_data=f"pay_{package_id}"
        ))
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="buy_stars"))
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery):
    await callback.answer("💳 Функция оплаты в разработке!", show_alert=True)


@router.callback_query(F.data == "my_purchases")
async def show_purchases(callback: CallbackQuery):
    text = """
📦 <b>Мои покупки</b>

У вас пока нет покупок.
Купите свой первый пакет звёзд!
"""
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="💬 Написать в поддержку",
        url="https://t.me/your_support"
    ))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    
    await callback.message.edit_text(SUPPORT_TEXT, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "privacy")
async def show_privacy(callback: CallbackQuery):
    await callback.message.edit_text(PRIVACY_TEXT, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "terms")
async def show_terms(callback: CallbackQuery):
    await callback.message.edit_text(TERMS_TEXT, reply_markup=get_back_keyboard())
    await callback.answer()


# Регистрируем роутер
dp.include_router(router)


# === Запуск ===
async def start_bot():
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


async def start_web():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    logger.info(f"Web server started on port {WEBAPP_PORT}")


async def main():
    logger.info("=" * 50)
    logger.info("🚀 Starting Telegram Stars Bot")
    logger.info("=" * 50)
    
    # Запускаем веб-сервер и бота параллельно
    await asyncio.gather(
        start_web(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
