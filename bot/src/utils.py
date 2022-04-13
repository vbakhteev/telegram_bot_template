import logging

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


def get_logger(is_prod: bool, name='bot'):
    logging.basicConfig(
        level=logging.INFO if is_prod else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger = logging.getLogger(name=name)
    if is_prod:
        for handler in logging.root.handlers:
            handler.addFilter(logging.Filter(name))
        logger.addHandler(logging.FileHandler("data/bot.log"))

    return logger
