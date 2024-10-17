import asyncio
import logging
import sys
from os import getenv
from config import key_t

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Bot token can be obtained via https://t.me/BotFather
TOKEN = key_t
dp = Dispatcher()

style_preset = ['3d-model', 'analog-film', 'anime', 'pixel-art', 'neon-punk', 'fantasy-art', 'comic-book']

class Form(StatesGroup):
    style_presets = State()
    prompt = State()


def get_style_keyboard():
    buttons = []
    for preset in style_preset:
        buttons.append(KeyboardButton(text=preset))
    keyboard = ReplyKeyboardMarkup(keyboard=[buttons])
    return keyboard

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}!")

@dp.message(Command('image'))
async def command_image_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Chose style preset:", reply_markup=get_style_keyboard())
    await state.set_state(Form.style_presets)

@dp.message(Form.style_presets)
async def process_presets(message: Message, state: FSMContext) -> None:
    await state.update_data(style_presets=message.text)
    await state.set_state(Form.prompt)
    await message.answer('Input prompt')

@dp.message(Form.prompt)
async def process_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    preset = data.get('style_presets')
    prompt = message.text
    await state.clear()
    await message.answer(f'Stay by please, loading {preset}, {prompt}')


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
