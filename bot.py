from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
import logging
import os
# Импортируем токен
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_name = State()

DB_FILE = os.path.abspath("shop.db")  # путь к базе данных
#Инициализирует базу данных, создает таблицу users, если она не существует. Записывает в логи начало инициализации, создание таблицы и закрытие соединения.
def init_db():
    conn = None
    try:
        if not os.path.exists(DB_FILE):
            logger.info("Файл базы данных не существует. Создаем новую базу данных.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE
            )
        """)
        conn.commit()
        logger.info("Таблица 'users' успешно создана или уже существует.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Соединение с базой данных закрыто.")
# Проверяем зарегистрирован ли пользователь с указанным email.
def check_user(email):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        logger.error(f"Ошибка при проверке пользователя: {e}")
        return False
    finally:
        if conn:
            conn.close()
# Регистрирует нового пользователя в базе данных.
def register_user(first_name, last_name, email):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?)",
                       (first_name, last_name, email))
        conn.commit()
        logger.info(f"Пользователь {email} зарегистрирован.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
    finally:
        if conn:
            conn.close()

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Каталог"))
    builder.add(KeyboardButton(text="Корзина"))
    builder.add(KeyboardButton(text="Поддержка"))
    return builder.as_markup(resize_keyboard=True)

# команда /start
@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    photo_path = os.path.abspath("logo.jpeg")
    logger.info(f"Попытка отправить фото по пути: {photo_path}")
    try:
        with open(photo_path, "rb") as photo:
            await message.answer_photo(
                photo=BufferedInputFile(photo.read(), filename="logo.jpeg"),
                caption=(
                    "Привет! Мы рады видеть тебя здесь!✨\n"
                    "В нашем боте ты найдешь самые стильные и качественные товары прямо из <b>Кореи</b>: "
                    "от косметики и моды до уникальных аксессуаров и вкусняшек.🇰🇷\n\n"
                    "Для регистрации введи свой email:"
                )
            )
            logger.info("Фото успешно отправлено.")
    except FileNotFoundError:
        logger.error(f"Файл {photo_path} не найден.")
        await message.answer(
            "Привет! Мы рады видеть тебя здесь!✨\n"
            "В нашем боте ты найдешь самые стильные и качественные товары прямо из <b>Кореи</b>: "
            "от косметики и моды до уникальных аксессуаров и вкусняшек.🇰🇷\n\n"
            "Для регистрации введи свой email:"
        )

    await state.set_state(RegistrationStates.waiting_for_email)

# ввод email
@dp.message(RegistrationStates.waiting_for_email)
async def register_email(message: types.Message, state: FSMContext):
    email = message.text
    if check_user(email):
        await message.answer("Этот email уже зарегистрирован. Пожалуйста, используй другой email.")
        return
    await state.update_data(email=email)
    await message.answer("Отлично! Теперь введи свое имя и фамилию (через пробел):")
    await state.set_state(RegistrationStates.waiting_for_name)
# ввод имени и фамилии
@dp.message(RegistrationStates.waiting_for_name)
async def register_name(message: types.Message, state: FSMContext):
    try:
        first_name, last_name = message.text.split(" ", 1)
        data = await state.get_data()
        email = data.get("email")
        register_user(first_name, last_name, email)

        await message.answer(
            "Спасибо за регистрацию! Ты получил скидку 20% на первый заказ.\n"
            "Теперь ты можешь выбрать товар:",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
# кнопка "Каталог"
@dp.message(lambda message: message.text == "Каталог")
async def show_catalog(message: types.Message):
    await message.answer("Потом здесь появиться ссылка на каталог с товаром, которая будет ввиде web-app")
#  кнопка "Корзина"
@dp.message(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message):
    await message.answer("Ваша корзина пуста.")
#  кнопка "Поддержка"
@dp.message(lambda message: message.text == "Поддержка")
async def show_support(message: types.Message):
    await message.answer("Свяжитесь с нами через Telegram: @support")
async def on_startup():
    logger.info("Запуск функции on_startup")
    init_db()
    logger.info("Бот запущен!")
async def on_shutdown():
    logger.info("Бот остановлен.")
async def main():
    await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
