from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import STAR_PACKAGES, WEBAPP_URL, SUPPORT_USERNAME


def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🛒 Купить звёзды",
            callback_data="buy_stars"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🌐 Открыть магазин",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📦 Мои покупки",
            callback_data="my_purchases"
        ),
        InlineKeyboardButton(
            text="💬 Поддержка",
            callback_data="support"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📜 Политика конфиденциальности",
            callback_data="privacy_policy"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Пользовательское соглашение",
            callback_data="terms_of_service"
        )
    )
    
    return builder.as_markup()


def get_packages_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for package in STAR_PACKAGES:
        bonus_text = f" +{package['bonus']}🎁" if package['bonus'] > 0 else ""
        builder.row(
            InlineKeyboardButton(
                text=f"⭐ {package['stars']}{bonus_text} — {package['price']} Stars",
                callback_data=f"package_{package['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
    )
    
    return builder.as_markup()


def get_payment_keyboard(package_id: int, price: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"💳 Оплатить {price} ⭐",
            pay=True
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад к пакетам",
            callback_data="buy_stars"
        )
    )
    
    return builder.as_markup()


def get_support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать в поддержку",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="❓ FAQ",
            callback_data="faq"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
    )
    
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад в меню",
            callback_data="back_to_main"
        )
    )
    
    return builder.as_markup()
