import enum
import os

from sqlalchemy import create_engine
from telegram import Update
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, PicklePersistence, ConversationHandler, MessageHandler, Filters,
    CallbackQueryHandler
)

from src.manager import Manager
from src.models import GroupType
from src.utils import get_logger, inline_keyboard, markup_keyboard, get_match_regex


class BUTTONS:
    create_group = "Создать Хаб"


class ConvState(enum.Enum):
    group_type_selected = enum.auto()


def start(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user

    if not manager.is_admin_registered(admin_id=user.id):
        # Register the user
        manager.register_admin(
            admin_id=user.id,
            fullname=user.full_name,
            username=user.username,
        )

    user.send_message("Бот администратор.\nМожно создать Хаб, проверять отчеты и давать участникам выходные")

    return main_menu(update, context)


def main_menu(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user

    group_names = ['хаб1', 'хаб2']
    keyboard = markup_keyboard(
        [[BUTTONS.create_group]] + [[group_name] for group_name in group_names]
    )

    user.send_message(
        text="Выбери действие или Хаб:",
        reply_markup=keyboard,
    )

    return ConversationHandler.END


###############
# Crete group #
###############


def choose_group_type(update: Update, context: CallbackContext) -> ConvState:
    group_types = {
        GroupType.reading: "Чтение",
        GroupType.sleeping: "Режим сна",
    }.values()

    keyboard = inline_keyboard(
        buttons=[[v] for k, v in group_types] + [["Отмена"]],
        callbacks=[[f'group_type_{k}'] for k, v in group_types] + [["cancel"]]
    )

    update.effective_user.send_message(
        text="Выбери тему Хаба",
        reply_markup=keyboard,
    )

    return ConvState.group_type_selected


def remove_group_creation(update: Update, context: CallbackContext) -> ConvState:
    query = update.callback_query
    query.answer()
    query.delete_message()

    return main_menu(update, context)


def create_group(update: Update, context: CallbackContext) -> ConvState:
    query = update.callback_query
    query.answer()
    query.delete_message()

    group_type = query.data.replace('group_type_', '')
    logger.info(group_type)

    return main_menu(update, context)


############
# Handlers #
############

# noinspection PyTypeChecker
def build_conv_handler():
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(choose_group_type, pattern="^create_group$"),
        ],
        states={
            ConvState.group_type_selected: [
                CallbackQueryHandler(create_group, pattern="^group_type_[.]+$"),
                CallbackQueryHandler(remove_group_creation, pattern="^cancel$"),
                MessageHandler(Filters.all, main_menu),
            ],
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
        MessageHandler(get_match_regex(BUTTONS.create_group), choose_group_type),

        MessageHandler(Filters.all, main_menu),
    ]

    for handler in handlers:
        dispatcher.add_handler(handler)


def main(admin_token: str, persistence_filename: str):
    logger.info(admin_token)
    persistence = PicklePersistence(filename=persistence_filename)
    updater = Updater(admin_token, persistence=persistence)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    logger.info("Start working!")
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == '__main__':
    is_prod = os.getenv("PROD", "false").lower() == "true"
    logger = get_logger(is_prod, file_path="bot_data/admin_bot.log")

    engine = create_engine(os.getenv('DB_URL'))
    manager = Manager(engine)

    main(
        admin_token=os.environ['ADMIN_TOKEN'],
        persistence_filename=os.getenv('PERSISTENCE', 'bot_data/admin_bot_persistence.data'),
    )
