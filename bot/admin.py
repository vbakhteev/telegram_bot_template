import enum
import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from telegram import Update, Bot
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, PicklePersistence, ConversationHandler, MessageHandler, Filters,
    CallbackQueryHandler, ChatMemberHandler
)
from telegram.utils import helpers

from src.manager import Manager
from src.models import GroupType
from src.utils import get_logger, inline_keyboard, markup_keyboard, get_match_regex, load_cities

pricing = [
    {'deposit': 800, 'rest_day_price': 400},
    {'deposit': 3000, 'rest_day_price': 1000},
    {'deposit': 8000, 'rest_day_price': 2000},
]

CHANNEL_NAME_PREFIX = 'HabHab '


class BUTTONS:
    create_group = "Создать Хаб"


class ConvState(enum.Enum):
    group_type_selected = enum.auto()
    requested_channel_creation = enum.auto()
    requested_deposit_size = enum.auto()
    requested_start_date = enum.auto()


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

    group_names = manager.get_admin_groups_names(admin_id=user.id)
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
    }.items()

    keyboard = inline_keyboard(
        buttons=[[v] for k, v in group_types] + [["Отмена"]],
        callbacks=[[f'group_type_{k.get_name()}'] for k, v in group_types] + [["cancel"]]
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


def choose_deposit_size(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user
    query = update.callback_query
    query.answer()
    query.delete_message()

    group_type = GroupType[query.data.replace('group_type_', '')]
    context.user_data['group_type'] = group_type

    keyboard = inline_keyboard(
        buttons=[["Депозит {}р, выходной {}р".format(p['deposit'], p['rest_day_price'])] for p in pricing],
        callbacks=[["pricing_{}_{}".format(p['deposit'], p['rest_day_price'])] for p in pricing],
    )

    user.send_message(
        text='Какой режим оплаты?',
        reply_markup=keyboard,
    )
    return ConvState.requested_deposit_size


def choose_start_date(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user
    query = update.callback_query
    query.answer()
    query.delete_message()

    deposit, rest_day_price = map(int, query.data.replace('pricing_', '').split('_'))
    context.user_data['deposit'] = deposit
    context.user_data['rest_day_price_to_bank'] = int(rest_day_price * 0.5)

    now = datetime.now()
    date_now = now.date()

    day_deltas = list(range(0 if now.hour < 14 else 1, 7))
    keyboard = inline_keyboard(
        buttons=[[
            (date_now + timedelta(days=day_delta)).strftime('%d %B')
        ] for day_delta in day_deltas],
        callbacks=[[f'day_delta_{day_delta}'] for day_delta in day_deltas],
    )

    user.send_message(
        text='Когда начало?',
        reply_markup=keyboard,
    )

    return ConvState.requested_start_date


def create_channel(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user
    query = update.callback_query
    query.answer()
    query.delete_message()

    day_delta = int(query.data.replace('day_delta_', ''))
    start_date = datetime.now().date() + timedelta(days=day_delta)

    group_id, group_name, invite = manager.create_group(
        admin_id=user.id,
        group_type=context.user_data.pop('group_type'),
        deposit=context.user_data.pop('deposit'),
        rest_day_price_to_bank=context.user_data.pop('rest_day_price_to_bank'),
        start_date=start_date,
        cities=cities,
    )
    context.user_data['group_id'] = group_id
    context.user_data['invite'] = invite
    context.user_data['group_name'] = group_name

    return ask_to_create_channel(update, context)


def ask_to_create_channel(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user

    channel_name = CHANNEL_NAME_PREFIX + context.user_data['group_name']
    user.send_message(
        text=f'''Создай приватный канал с названием

<b>{channel_name}</b>

Нужно добавить этого бота @{context.bot.username} в администраторы с дефолтными настройками''',
        reply_markup=markup_keyboard([['Готово']], one_time_keyboard=True),
        parse_mode='HTML',
    )

    return ConvState.requested_channel_creation


def join_channel(update: Update, context: CallbackContext):
    channel = update.my_chat_member.chat
    channel_name = channel.title

    if not channel_name.startswith(CHANNEL_NAME_PREFIX):
        logger.warn(
            f"Admin bot was added to channel `{channel_name}`, but name is not started from `{CHANNEL_NAME_PREFIX}`"
        )
        return

    group_name = channel_name.replace(CHANNEL_NAME_PREFIX, '')
    channel_is_set = manager.set_channel_id_by_name(
        channel_id=channel.id,
        group_name=group_name,
    )

    if not channel_is_set:
        logger.warn(f"Admin bot was added to channel `{group_name}`, but there is no Hab with such name")
        return

    update.effective_user.send_message("Успех! Жми Готово!")


def finish_creation(update: Update, context: CallbackContext) -> ConvState:
    user = update.effective_user
    group_id = context.user_data['group_id']

    if not manager.is_channel_set(group_id=group_id):
        return ask_to_create_channel(update, context)

    invite = context.user_data.pop('invite')
    url = helpers.create_deep_linked_url(
        bot_username=client_bot.username,
        payload=str(invite),
    )
    user.send_message(
        text=f'''Хаб успешно создан!
Осталось создать чат для канала, добавить туда участников.

Еще отправь им ссылку, чтобы зарегистрировались в боте:
{url}''',
    )

    return main_menu(update, context)


############
# Handlers #
############

# noinspection PyTypeChecker
def build_conv_handler():
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(choose_deposit_size, pattern="^group_type_(.)+"),
        ],
        states={
            ConvState.group_type_selected: [
                MessageHandler(Filters.all, main_menu),
            ],
            ConvState.requested_deposit_size: [
                CallbackQueryHandler(choose_start_date, pattern='^pricing_[0-9]+_[0-9]+$'),
            ],
            ConvState.requested_start_date: [
                CallbackQueryHandler(create_channel, pattern='^day_delta_[0-9]+'),
            ],
            ConvState.requested_channel_creation: [
                MessageHandler(Filters.all, finish_creation),
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

        ChatMemberHandler(join_channel),
        CallbackQueryHandler(remove_group_creation, pattern="^cancel$"),
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
