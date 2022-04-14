import os

from minio import Minio
from sqlalchemy import create_engine
from telegram import Update
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, PicklePersistence,
)

from src.manager import Manager
from src.utils import get_logger, put_file_to_storage, get_file_from_storage


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    # Get profile picture file
    photos = user.get_profile_photos()
    file = photos.photos[0][-1].get_file() if photos['total_count'] > 0 else None

    if not manager.is_user_registered(user_id=user.id):
        # Register the user
        manager.register_user(
            user_id=user.id,
            fullname=user.full_name,
            username=user.username,
        )

        # Save image to minio
        if file is not None:
            put_file_to_storage(
                client=minio_client,
                file=file,
                bucket_name='profilepics',
                extension='jpg',
            )

        msg = f'Welcome {user.full_name}'
        logger.info("Registered user %s - %s - %s", user.id, user.full_name, user.username)
    else:
        # Load image from minio and send to user
        if file is not None:
            response = get_file_from_storage(
                client=minio_client,
                file_name=str(file['file_unique_id']) + '.jpg',
                bucket_name='profilepics',
            )
            user.send_photo(photo=response)

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
    is_prod = os.getenv("PROD", "false").lower() == "true"
    logger = get_logger(is_prod, file_path="bot_data/bot.log")

    minio_client = Minio(
        os.getenv("MINIO_URL"),
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,
    )
    if not minio_client.bucket_exists("profilepics"):
        minio_client.make_bucket("profilepics")

    engine = create_engine(os.getenv('DB_URL'))
    manager = Manager(engine)

    main(
        token=os.getenv('TOKEN'),
        persistence_filename=os.getenv('PERSISTENCE', 'bot_data/bot_persistence.data'),
    )
