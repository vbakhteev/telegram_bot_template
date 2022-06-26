import enum
import os

from sqlalchemy import create_engine
from telegram import Update, Bot
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, PicklePersistence, ConversationHandler, MessageHandler, Filters
)

from src.manager import Manager
from src.utils import get_logger, load_cities, markup_keyboard


class ConvState(enum.Enum):
    pass


def start(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user

    if not manager.is_user_registered(user_id=user.id):
        # Register the user
        manager.register_user(
            user_id=user.id,
            fullname=user.full_name,
            username=user.username,
        )

        user.send_message("""Это бот Отчетыватель
    
- Принимает ежедневные отчеты
- Можно настроить напоминания"""
                          )
        # TODO timezone

        # TODO invitation

    return


def main_menu(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user

    groups_names = manager.get_user_groups(user_id=user.id)
    keyboard = markup_keyboard(
        buttons=[[group_name] for group_name in groups_names],
    )
    user.send_message(
        text="Выбери Хаб:",
        reply_markup=keyboard,
    )

    return ConversationHandler.END


############
# Handlers #
############

# noinspection PyTypeChecker
def build_conv_handler():
    conv_handler = ConversationHandler(
        entry_points=[
        ],
        states={
        },
        fallbacks=[
            MessageHandler(Filters.all, main_menu),
        ],
    )
    return conv_handler


def add_handlers(dispatcher):
    dispatcher.add_handler(build_conv_handler())

    handlers = [
        CommandHandler("start", start),

        MessageHandler(Filters.all, main_menu),
    ]

    for handler in handlers:
        dispatcher.add_handler(handler)


def main(admin_token: str, persistence_filename: str):
    logger.info(admin_token)
    persistence = PicklePersistence(filename=persistence_filename)
    updater = Updater(admin_token, persistence=persistence)
    add_handlers(dispatcher=updater.dispatcher)

    logger.info("Start working!")
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == '__main__':
    is_prod = os.getenv("PROD", "false").lower() == "true"
    logger = get_logger(is_prod, file_path="bot_data/admin_bot.log")

    cities = load_cities('cities.csv')

    engine = create_engine(os.getenv('DB_URL'))
    manager = Manager(engine)

    client_bot = Bot(os.environ['CLIENT_TOKEN'])

    main(
        admin_token=os.environ['ADMIN_TOKEN'],
        persistence_filename=os.getenv('PERSISTENCE', 'bot_data/admin_bot_persistence.data'),
    )
