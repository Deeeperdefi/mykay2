import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import pytz

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot states
class Form(StatesGroup):
    name = State()
    surname = State()
    email = State()

# Your token list
TOKENS = [
    "J7#kL9@mN2!pQ", "xY5$fT8&zR1*wP", "qW3^bV6%nM4#sX", "8K@dH5!jL9$rF2",
    # ... (rest of your tokens)
]

# Database setup would be similar to your original code
# Initialize bot and dispatcher
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Welcome to our Airdrop Bot! 🎉\n\nWhat is your first name?")

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.reply("Great! What is your surname?")

@dp.message_handler(state=Form.surname)
async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await Form.next()
    await message.reply("Almost done! What is your email address?")

@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        # Here you would add your token distribution logic
        token = "TEST_TOKEN"  # Replace with your distribution logic
        await message.reply(f"🎉 Here's your token: {token}")
    await state.finish()

async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_CHAT_ID, text="Bot started")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
