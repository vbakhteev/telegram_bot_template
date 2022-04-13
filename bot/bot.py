import os

from sqlalchemy import create_engine
from telegram import Update
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, PicklePersistence,
)

from src.manager import Manager
from src.utils import get_logger


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    if not manager.is_user_registered(user_id=user.id):
        manager.register_user(
            user_id=user.id,
            fullname=user.full_name,
            username=user.username,
        )
        msg = f'Welcome {user.full_name}'

        logger.info("Registered user %s - %s - %s", user.id, user.full_name, user.username)
    else:
        msg = f'Nice to see you again, {user.full_name}'

    update.message.reply_text(text=msg)


def main(token, persistence_filename: str):
    persistence = PicklePersistence(filename=persistence_filename)
    updater = Updater(token, persistence=persistence)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    logger.info("Start working!")
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == '__main__':
    is_prod = os.getenv('PROD', False)
    logger = get_logger(is_prod, file_path="bot_data/bot.log")

    engine = create_engine(os.getenv('DB_URL'))
    manager = Manager(engine)

    token = os.getenv('TOKEN')
    persistence_filename = os.getenv('PERSISTENCE', 'bot_data/bot_persistence.data')
    main(token, persistence_filename)
