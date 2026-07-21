import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.filters import Command
from userdb import add_user,get_user
from aiogram import Router
from aiogram.types import Message
from walletdb import add_wallet,get_wallet,add_money,remove_money,get_trans
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

dp = Dispatcher()

class WalletState(StatesGroup):
    add_money = State()
    remove_money = State()

#MENU
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Кошелек"),
            KeyboardButton(text="История"),
        ],
        [
            KeyboardButton(text="➕ Пополнить"),
            KeyboardButton(text="➖ Снять")
        ]
    ],
    resize_keyboard=True
)
money_status = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Еда"),
            KeyboardButton(text="Электроника"),
            KeyboardButton(text="Одежда"),

        ]
    ],
    resize_keyboard=True
)
#BUTTON

@dp.message(lambda message: message.text == "История")
async def history_button(message: Message):

    user_id = message.from_user.id
    name = message.from_user.first_name
    history = get_trans(user_id)

    if not history:
        await message.answer(
            parse_mode="HTML"
        )
        return 

    message_text = f"<b>Твоия история  {name}, \nКоличество операций: {len(history)}</b>\n\n"
    for amount, type, date in history: 
        emoji = "🟢" if type == 'Пополнение' else "🔴"
        real_amount = amount / 100 
        message_text += f"{emoji} <b>{type}:</b> {real_amount:.2f}€ | 🗓 {date}\n"
        
    await message.answer(
        text=message_text,
        parse_mode="HTML"
    )




@dp.message(lambda message: message.text == "Кошелек")
async def wallet_button(message: Message):

    user_id = message.from_user.id

    wallet = get_wallet(user_id)

    if wallet is None:
        add_wallet(user_id)
        wallet = get_wallet(user_id)

    money = wallet[0] / 100

    await message.answer(
        f"💰 Баланс: {money:.2f}€"
    )

@dp.message(lambda message: message.text == "➕ Пополнить")
async def add_button(message: Message, state: FSMContext):

    await message.answer("Введите сумму пополнения:")
    await state.set_state(WalletState.add_money)

@dp.message(lambda message: message.text == "➖ Снять")
async def remove_button(message: Message, state: FSMContext):

    await message.answer("Введите сумму снятия:")
    await state.set_state(WalletState.remove_money)


#STATE
@dp.message(WalletState.add_money)
async def add_amount(message: Message, state: FSMContext):

    user_id = message.from_user.id

    try:
        money = float(message.text)
        money = int(money * 100)

    except:
        await message.answer("Введите число")
        return

    add_money(user_id, money)
    wallet = get_wallet(user_id)
    balance = wallet[0] / 100

    await message.answer(
        f"💰 Баланс: {balance:.2f}€",
        reply_markup=main_keyboard
    )

    await state.clear()

@dp.message(WalletState.remove_money)
async def remove_amount(message: Message, state: FSMContext):

    user_id = message.from_user.id

    try:
        money = float(message.text)
        money = int(money * 100)

    except:
        await message.answer("Введите число")
        return

    wallet = get_wallet(user_id)

    if money > wallet[0]:
        await message.answer("Недостаточно денег")
        await state.clear()
        return

    remove_money(user_id, money)

    wallet = get_wallet(user_id)
    balance = wallet[0] / 100

    await message.answer(
        f"💰 Баланс: {balance:.2f}€",
        reply_markup=main_keyboard
    )

    await state.clear()


@dp.message(CommandStart())
async def command_start_handler(message: Message):

    user_id = message.from_user.id
    name = message.from_user.first_name

    add_user(user_id, name)

    if not get_wallet(user_id):
        add_wallet(user_id)

    await message.answer(
        f"Привет, {name}",
        reply_markup=main_keyboard
    )

@dp.message(Command("info"))
async def help_handler(message: Message):
    await message.answer("Это сообщение от бота по команде /info")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())