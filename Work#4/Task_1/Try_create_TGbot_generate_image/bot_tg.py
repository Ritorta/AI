import asyncio # Импортируем библиотеку asyncio для работы с асинхронным кодом
import logging # Импортируем библиотеку logging для работы с логированием
import sys # Импортируем библиотеку sys для работы с системными параметрами и функциями
from os import getenv # Импортируем функцию getenv из модуля os

from aiogram import Bot, Dispatcher, html # Импортируем классы Bot, Dispatcher и html из библиотеки aiogram
from aiogram.client.default import DefaultBotProperties # Импортируем класс DefaultBotProperties из aiogram
from aiogram.enums import ParseMode # Импортируем перечисление ParseMode из aiogram
from aiogram.filters import CommandStart, Command # Импортируем фильтры CommandStart и Command из aiogram
from aiogram.fsm.state import StatesGroup, State # Импортируем классы StatesGroup и State для работы с FSM
from aiogram.fsm.context import FSMContext # Импортируем класс FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, URLInputFile # Импортируем некоторые типы сообщений из aiogram
from loader_image import start # Импортируем функцию start из модуля loader_image

import importlib.util # Импорт модуля importlib.util для импорта модуля из файла

# Импорта файла config.py
spec = importlib.util.spec_from_file_location("config", "C:/Users/Esdesu/Documents/Материалы по обучению/Обучение Ai/Folder_confing/config.py")
# Импорт модуля config из файла
config = importlib.util.module_from_spec(spec)
# Загрузка модуля config
spec.loader.exec_module(config)
# Получение ключа из модуля config
key_t = config.key_t

# Используем создание бота через телеграмм бота https://t.me/BotFather
# Присваиваем переменной TOKEN полученный токен бота
TOKEN = key_t

# Создаем диспетчер для обработки сообщений
dp = Dispatcher()

# Создаём набор присетов из сервиса prodia.com
style_preset = ['3d-model', 'analog-film', 'anime', 'pixel-art', 'neon-punk', 'fantasy-art', 'comic-book']

# Определяем класс StatesGroup для работы с состояниями в FSM
class Form(StatesGroup):
    style_presets = State()
    prompt = State()

# Функция для создания клавиатуры выбора стиля обработки изображения
def get_style_keyboard():
    buttons = []
    for preset in style_preset:
        buttons.append(KeyboardButton(text=preset))
    keyboard = ReplyKeyboardMarkup(keyboard=[buttons])
    return keyboard

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}!")

# Обработчик команды /image
@dp.message(Command('image'))
async def command_image_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"Chose style preset:", reply_markup=get_style_keyboard())
    await state.set_state(Form.style_presets)

# Обработчик для выбора стиля обработки изображения
@dp.message(Form.style_presets)
async def process_presets(message: Message, state: FSMContext) -> None:
    await state.update_data(style_presets=message.text)
    await state.set_state(Form.prompt)
    await message.answer('Input prompt')

# Обработчик для ввода запроса
@dp.message(Form.prompt)
async def process_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    preset = data.get('style_presets')
    prompt = message.text
    await state.clear()
    await message.answer(f'Stay by please, loading {preset}, {prompt}')
    try:
        result_url = start(prompt, preset)
        if result_url: 
            img = URLInputFile(result_url)
            await message.answer_photo(photo=img)
    except Exception as e:
        await message.answer(f'Error...!: {str(e)}')

# Определение обработчика сообщений echo_handler, который принимает сообщение и отправляет его обратно в чат
@dp.message()
async def echo_handler(message: Message, state: FSMContext) -> None:
    if message.text.lower() in ['/start', '/image', '/help']:
        if message.text.lower() == '/help':
            await message.answer("Available commands:\n/start - greeting\n/image - choose image processing style\n/help - get list of commands")
        elif message.text.lower() == '/start':
            await message.answer(f"Hello, {message.from_user.first_name}!")
        elif message.text.lower() == '/image':
            await message.answer(f"Choose style preset:", reply_markup=get_style_keyboard())
            await state.set_state(Form.style_presets)
    else:
        await message.answer("Invalid command.")

# Основная функция, запускающая бота и начинающая опрос сообщений
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

# Запуск основной функции при запуске скрипта
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
