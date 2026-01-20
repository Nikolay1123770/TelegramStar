import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# ============================================
# КОНФИГУРАЦИЯ
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
WEBAPP_PORT = int(os.getenv("PORT", 3000))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================
# ВСТРОЕННЫЙ HTML/CSS/JS
# ============================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stars Shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root { --bg: #0f0f0f; --card: #1a1a1a; --text: #fff; --accent: #7c3aed; --gold: #ffd700; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
        .app { max-width: 500px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px; background: linear-gradient(135deg, #7c3aed, #a855f7); border-radius: 20px; margin-bottom: 20px; }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header p { opacity: 0.9; }
        .user-card { display: flex; align-items: center; gap: 15px; background: var(--card); padding: 20px; border-radius: 16px; margin-bottom: 20px; }
        .user-avatar { width: 50px; height: 50px; background: linear-gradient(135deg, var(--gold), #b8860b); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .user-name { font-weight: 600; font-size: 18px; }
        .user-id { color: #888; font-size: 14px; }
        h2 { font-size: 20px; margin-bottom: 15px; }
        .packages-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 30px; }
        .package-card { background: var(--card); border-radius: 16px; padding: 20px; text-align: center; cursor: pointer; transition: transform 0.2s; }
        .package-card:hover { transform: translateY(-2px); }
        .package-card.popular { border: 2px solid var(--accent); }
        .package-stars { font-size: 32px; margin-bottom: 8px; }
        .package-amount { font-size: 24px; font-weight: 700; color: var(--gold); }
        .package-bonus { background: linear-gradient(135deg, var(--gold), #b8860b); color: #000; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; margin: 8px 0; }
        .package-price { color: #888; font-size: 14px; }
        .features-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 30px; }
        .feature { background: var(--card); border-radius: 12px; padding: 15px 10px; text-align: center; }
        .feature-icon { font-size: 24px; display: block; margin-bottom: 5px; }
        .feature-title { font-size: 11px; color: #888; }
        .footer { text-align: center; padding: 20px 0; border-top: 1px solid #333; }
        .footer a { color: #888; text-decoration: none; font-size: 12px; margin: 0 10px; }
        .footer a:hover { color: var(--accent); }
    </style>
</head>
<body>
    <div class="app">
        <header class="header">
            <h1>⭐ Stars Shop</h1>
            <p>Покупайте Telegram Stars выгодно</p>
        </header>

        <div class="user-card">
            <div class="user-avatar">👤</div>
            <div>
                <div class="user-name" id="userName">Гость</div>
                <div class="user-id" id="userId">ID: —</div>
            </div>
        </div>

        <h2>🛒 Выберите пакет</h2>
        <div class="packages-grid" id="packages"></div>

        <h2>✨ Почему мы?</h2>
        <div class="features-grid">
            <div class="feature"><span class="feature-icon">⚡</span><span class="feature-title">Мгновенно</span></div>
            <div class="feature"><span class="feature-icon">🔒</span><span class="feature-title">Безопасно</span></div>
            <div class="feature"><span class="feature-icon">🎁</span><span class="feature-title">Бонусы</span></div>
            <div class="feature"><span class="feature-icon">💬</span><span class="feature-title">Поддержка</span></div>
        </div>

        <footer class="footer">
            <a href="/privacy">Политика конфиденциальности</a>
            <a href="/terms">Пользовательское соглашение</a>
        </footer>
    </div>

    <script>
        const tg = window.Telegram?.WebApp;
        const packages = [
            { id: 1, stars: 50, price: 50, bonus: 0 },
            { id: 2, stars: 100, price: 100, bonus: 5, popular: true },
            { id: 3, stars: 250, price: 250, bonus: 15 },
            { id: 4, stars: 500, price: 500, bonus: 50, popular: true },
            { id: 5, stars: 1000, price: 1000, bonus: 150 }
        ];

        if (tg) {
            tg.ready();
            tg.expand();
            const user = tg.initDataUnsafe?.user;
            if (user) {
                document.getElementById('userName').textContent = user.first_name + (user.last_name ? ' ' + user.last_name : '');
                document.getElementById('userId').textContent = 'ID: ' + user.id;
            }
        }

        document.getElementById('packages').innerHTML = packages.map(p => `
            <div class="package-card ${p.popular ? 'popular' : ''}" onclick="buy(${p.id})">
                <div class="package-stars">⭐</div>
                <div class="package-amount">${p.stars}</div>
                ${p.bonus ? `<div class="package-bonus">+${p.bonus} бонус</div>` : '<div style="height:24px"></div>'}
                <div class="package-price">${p.price} Stars</div>
            </div>
        `).join('');

        function buy(id) {
            const p = packages.find(x => x.id === id);
            if (tg) {
                tg.showConfirm('Купить ' + p.stars + ' ⭐ за ' + p.price + ' Stars?', ok => {
                    if (ok) tg.sendData(JSON.stringify({ action: 'buy', package_id: id }));
                });
            } else {
                alert('Покупка ' + p.stars + ' Stars');
            }
        }
    </script>
</body>
</html>
"""

PRIVACY_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Политика конфиденциальности</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f0f0f; color: #fff; min-height: 100vh; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { font-size: 24px; margin-bottom: 20px; color: #7c3aed; }
        h3 { margin: 20px 0 10px; color: #a855f7; }
        p { color: #888; line-height: 1.6; margin-bottom: 10px; }
        .back { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #7c3aed; color: #fff; text-decoration: none; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📜 Политика конфиденциальности</h1>
        <h3>1. Сбор данных</h3>
        <p>Мы собираем только необходимые данные: Telegram ID, Username, историю покупок.</p>
        <h3>2. Использование данных</h3>
        <p>Данные используются для обработки заказов, поддержки и улучшения сервиса.</p>
        <h3>3. Защита данных</h3>
        <p>Мы не передаём данные третьим лицам. Все данные хранятся в зашифрованном виде.</p>
        <h3>4. Удаление данных</h3>
        <p>Вы можете запросить удаление данных через поддержку.</p>
        <a href="/" class="back">← Назад</a>
    </div>
</body>
</html>
"""

TERMS_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Пользовательское соглашение</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f0f0f; color: #fff; min-height: 100vh; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { font-size: 24px; margin-bottom: 20px; color: #7c3aed; }
        h3 { margin: 20px 0 10px; color: #a855f7; }
        p { color: #888; line-height: 1.6; margin-bottom: 10px; }
        .back { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #7c3aed; color: #fff; text-decoration: none; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Пользовательское соглашение</h1>
        <h3>1. Общие положения</h3>
        <p>Используя данный сервис, вы соглашаетесь с условиями ниже.</p>
        <h3>2. Услуги</h3>
        <p>Мы предоставляем услуги по продаже Telegram Stars с автоматической доставкой.</p>
        <h3>3. Оплата</h3>
        <p>Оплата через Telegram Payments. Все платежи окончательные.</p>
        <h3>4. Ограничения</h3>
        <p>Запрещено мошенничество. Нарушители блокируются без возврата средств.</p>
        <a href="/" class="back">← Назад</a>
    </div>
</body>
</html>
"""

# ============================================
# ВЕБ-СЕРВЕР
# ============================================

async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')

async def handle_privacy(request):
    return web.Response(text=PRIVACY_HTML, content_type='text/html')

async def handle_terms(request):
    return web.Response(text=TERMS_HTML, content_type='text/html')

async def handle_health(request):
    return web.json_response({"status": "ok"})

# ============================================
# TELEGRAM BOT
# ============================================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

# Пакеты звёзд
PACKAGES = [
    {"id": 1, "stars": 50, "price": 50, "bonus": 0},
    {"id": 2, "stars": 100, "price": 100, "bonus": 5},
    {"id": 3, "stars": 250, "price": 250, "bonus": 15},
    {"id": 4, "stars": 500, "price": 500, "bonus": 50},
    {"id": 5, "stars": 1000, "price": 1000, "bonus": 150},
]

WELCOME = """
🌟 <b>Добро пожаловать в магазин Telegram Stars!</b>

⭐ Моментальная доставка
🎁 Выгодные бонусы  
🔒 Безопасные платежи
💬 Поддержка 24/7

Выберите действие 👇
"""

PRIVACY = """
📜 <b>Политика конфиденциальности</b>

<b>1. Сбор данных</b>
Telegram ID, Username, история покупок

<b>2. Использование</b>
Обработка заказов и поддержка

<b>3. Защита</b>
Данные не передаются третьим лицам

<b>4. Удаление</b>
Запрос через поддержку
"""

TERMS = """
📋 <b>Пользовательское соглашение</b>

<b>1. Услуги</b>
Продажа Telegram Stars с автодоставкой

<b>2. Оплата</b>
Через Telegram Payments, окончательная

<b>3. Правила</b>
Мошенничество = бан без возврата
"""

SUPPORT = """
💬 <b>Поддержка</b>

📩 @your_support
⏰ Ответ: до 1 часа
"""


def main_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛒 Купить звёзды", callback_data="buy"))
    b.row(
        InlineKeyboardButton(text="📦 Покупки", callback_data="purchases"),
        InlineKeyboardButton(text="💬 Поддержка", callback_data="support")
    )
    b.row(InlineKeyboardButton(text="📜 Конфиденциальность", callback_data="privacy"))
    b.row(InlineKeyboardButton(text="📋 Соглашение", callback_data="terms"))
    return b.as_markup()


def packages_kb():
    b = InlineKeyboardBuilder()
    for p in PACKAGES:
        bonus = f" +{p['bonus']}🎁" if p['bonus'] else ""
        b.row(InlineKeyboardButton(
            text=f"⭐ {p['stars']}{bonus} — {p['price']} Stars",
            callback_data=f"pkg_{p['id']}"
        ))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
    return b.as_markup()


def back_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
    return b.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME, reply_markup=main_kb())


@router.callback_query(F.data == "back")
async def go_back(cb: CallbackQuery):
    await cb.message.edit_text(WELCOME, reply_markup=main_kb())
    await cb.answer()


@router.callback_query(F.data == "buy")
async def show_packages(cb: CallbackQuery):
    await cb.message.edit_text("🛒 <b>Выберите пакет:</b>", reply_markup=packages_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("pkg_"))
async def select_pkg(cb: CallbackQuery):
    pkg_id = int(cb.data.split("_")[1])
    pkg = next((p for p in PACKAGES if p["id"] == pkg_id), None)
    if pkg:
        bonus = f" + {pkg['bonus']} бонус" if pkg['bonus'] else ""
        text = f"⭐ <b>{pkg['stars']}{bonus}</b>\n💰 Цена: {pkg['price']} Stars\n\n✅ Оплата в разработке"
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="buy"))
        await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data == "purchases")
async def show_purchases(cb: CallbackQuery):
    await cb.message.edit_text("📦 <b>Ваши покупки</b>\n\nПока пусто", reply_markup=back_kb())
    await cb.answer()


@router.callback_query(F.data == "support")
async def show_support(cb: CallbackQuery):
    await cb.message.edit_text(SUPPORT, reply_markup=back_kb())
    await cb.answer()


@router.callback_query(F.data == "privacy")
async def show_privacy(cb: CallbackQuery):
    await cb.message.edit_text(PRIVACY, reply_markup=back_kb())
    await cb.answer()


@router.callback_query(F.data == "terms")
async def show_terms(cb: CallbackQuery):
    await cb.message.edit_text(TERMS, reply_markup=back_kb())
    await cb.answer()


dp.include_router(router)

# ============================================
# ЗАПУСК
# ============================================

async def start_web():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/privacy', handle_privacy)
    app.router.add_get('/terms', handle_terms)
    app.router.add_get('/health', handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
    await site.start()
    logger.info(f"🌐 Web server on port {WEBAPP_PORT}")


async def start_bot():
    logger.info("🤖 Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    logger.info("=" * 40)
    logger.info("🚀 TELEGRAM STARS BOT")
    logger.info("=" * 40)
    
    await asyncio.gather(
        start_web(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
