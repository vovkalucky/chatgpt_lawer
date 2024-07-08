import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.handlers import user_handlers, admin_handlers, voice_handlers, other_handlers
from bot.keyboards.set_menu import set_main_menu
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config_data.config import load_config


#async def on_startup():
    #await db_start()
    #pass


async def main() -> None:
    # Создаем экземпляр логгера
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Создаем handler
    handler = TimedRotatingFileHandler(f'logs/bot_logs.log', when='D', backupCount=4)

    # Настройка формата сообщений
    # formatter = logging.Formatter('%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    # handler.setFormatter(formatter)

    # Добавляем handler к логгеру
    logger.addHandler(handler)

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO, #WARNING
        #filename='logs/bot_logs.log',
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
             '%(lineno)d - %(name)s - %(message)s'
    )
    print(logger.handlers)

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)

    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_routers(user_handlers.router, voice_handlers.router,
                     admin_handlers.router, other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    # Регистрация функции, которая сработает при запуске бота
    #dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as _ex:
        print(f'There is exception - {_ex}')



# Запускаем поллинг
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stop bot")
