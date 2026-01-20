from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot.keyboards.inline import get_main_keyboard
from bot.utils.texts import WELCOME_TEXT
from bot.database.db import db

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    # Сохраняем пользователя в БД
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        text=WELCOME_TEXT,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        text=WELCOME_TEXT,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
