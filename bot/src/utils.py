import logging
import random
from typing import Optional, List, Tuple

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters


def get_match_regex(*strs_to_match):
    s = '|'.join(strs_to_match)
    return Filters.regex(f'^({s})$')


def todict(obj):
    """Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ("_sa_adapter", "_sa_instance_state")
    return {
        k: v
        for k, v in vars(obj).items()
        if not k.startswith("_") and not any(hasattr(v, a) for a in excl)
    }


def get_logger(is_prod: bool, file_path: Optional[str] = None, name='bot'):
    logging.basicConfig(
        level=logging.INFO if is_prod else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger = logging.getLogger(name=name)
    if is_prod:
        for handler in logging.root.handlers:
            handler.addFilter(logging.Filter(name))
        logger.addHandler(logging.FileHandler(file_path or 'bot.log'))

    return logger


def markup_keyboard(
        buttons: List[List[str]], one_time_keyboard=False
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(y) for y in x] for x in buttons],
        one_time_keyboard=one_time_keyboard,
    )


def inline_keyboard(
        buttons: List[List[str]], callbacks: List[List[str]]
) -> InlineKeyboardMarkup:
    keyboard = []
    for buttons_row, callbacks_row in zip(buttons, callbacks):
        keyboard.append(
            [
                inline_button(button, callback)
                for button, callback in zip(buttons_row, callbacks_row)
            ]
        )
    return InlineKeyboardMarkup(keyboard)


def inline_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def generate_invite() -> int:
    return random.randint(0, 2 ** 32 - 1)


def load_cities(path) -> List[Tuple[str, str]]:
    cities = []
    with open(path) as f:
        for line in f:

            flag, city = line.strip().split(',')
            cities.append((flag, city))

    return cities
