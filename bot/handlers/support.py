from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from bot.keyboards.inline import get_support_keyboard, get_back_keyboard
from bot.utils.texts import SUPPORT_TEXT, PRIVACY_POLICY, TERMS_OF_SERVICE
from bot.config import SUPPORT_USERNAME

router = Router()


@router.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    await callback.message.edit_text(
        text=SUPPORT_TEXT.format(support_username=SUPPORT_USERNAME),
        reply_markup=get_support_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "privacy_policy")
async def show_privacy(callback: CallbackQuery):
    await callback.message.edit_text(
        text=PRIVACY_POLICY.format(date=datetime.now().strftime("%d.%m.%Y")),
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "terms_of_service")
async def show_terms(callback: CallbackQuery):
    await callback.message.edit_text(
        text=TERMS_OF_SERVICE.format(date=datetime.now().strftime("%d.%m.%Y")),
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    faq_text = """
❓ <b>Часто задаваемые вопросы</b>

<b>Q: Как быстро приходят звёзды?</b>
A: Моментально после оплаты.

<b>Q: Могу ли я подарить звёзды другу?</b>
A: Да, укажите @username получателя при покупке.

<b>Q: Безопасна ли оплата?</b>
A: Абсолютно. Мы используем официальные Telegram Payments.

<b>Q: Есть ли ограничения на покупку?</b>
A: Нет ограничений. Покупайте столько, сколько нужно.

<b>Q: Что делать, если звёзды не пришли?</b>
A: Напишите в поддержку с ID транзакции.
"""
    await callback.message.edit_text(
        text=faq_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
