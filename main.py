import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token="7645921921:AAGeyruHdvJOrenHp6CG06hyycvbpwjMTnY", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Запуск бота
async def main():
    # Регистрируем обработчики
    handlers.register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())