from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiogram.exceptions import TelegramBadRequest

from bot.keyboards.inline import get_packages_keyboard, get_back_keyboard
from bot.utils.texts import PACKAGES_TEXT, PAYMENT_SUCCESS, PAYMENT_PENDING
from bot.config import STAR_PACKAGES
from bot.database.db import db

router = Router()


@router.callback_query(F.data == "buy_stars")
async def show_packages(callback: CallbackQuery):
    await callback.message.edit_text(
        text=PACKAGES_TEXT,
        reply_markup=get_packages_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("package_"))
async def select_package(callback: CallbackQuery):
    package_id = int(callback.data.split("_")[1])
    package = next((p for p in STAR_PACKAGES if p["id"] == package_id), None)
    
    if not package:
        await callback.answer("Пакет не найден", show_alert=True)
        return
    
    # Создаём запись о покупке
    purchase_id = await db.create_purchase(
        user_id=callback.from_user.id,
        package_id=package_id,
        stars_amount=package["stars"],
        bonus_amount=package["bonus"],
        price=package["price"]
    )
    
    # Отправляем инвойс для оплаты Telegram Stars
    prices = [LabeledPrice(label="Telegram Stars", amount=package["price"])]
    
    try:
        await callback.message.answer_invoice(
            title=f"⭐ {package['stars']} Telegram Stars",
            description=f"Пакет из {package['stars']} звёзд" + 
                       (f" + {package['bonus']} бонусных" if package['bonus'] > 0 else ""),
            payload=f"purchase_{purchase_id}",
            currency="XTR",  # Telegram Stars
            prices=prices,
            start_parameter=f"buy_{package_id}"
        )
        await callback.answer()
    except TelegramBadRequest as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    # Подтверждаем возможность оплаты
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    # Извлекаем ID покупки
    purchase_id = int(payload.split("_")[1])
    
    # Обновляем статус покупки
    await db.complete_purchase(
        purchase_id=purchase_id,
        telegram_payment_id=payment.telegram_payment_charge_id
    )
    
    # Получаем информацию о пакете
    # (в реальном проекте лучше хранить это в БД)
    package = None
    for p in STAR_PACKAGES:
        if p["price"] == payment.total_amount:
            package = p
            break
    
    if package:
        await message.answer(
            text=PAYMENT_SUCCESS.format(
                stars=package["stars"],
                bonus=package["bonus"],
                total=package["stars"] + package["bonus"]
            ),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "my_purchases")
async def show_purchases(callback: CallbackQuery):
    purchases = await db.get_user_purchases(callback.from_user.id)
    
    if not purchases:
        text = "📦 <b>Мои покупки</b>\n\nУ вас пока нет покупок."
    else:
        text = "📦 <b>Мои покупки</b>\n\n"
        for i, p in enumerate(purchases, 1):
            text += f"{i}. ⭐ {p['stars_amount']}+{p['bonus_amount']} — {p['completed_at'][:10]}\n"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
