import io
import logging
from typing import Optional

from minio import Minio
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


def put_file_to_storage(client: Minio, file, bucket_name: str, extension: str) -> None:
    f = io.BytesIO(file.download_as_bytearray())

    client.put_object(
        bucket_name=bucket_name,
        object_name=file['file_unique_id'] + '.' + extension,
        data=f, length=file['file_size'],
    )


def get_file_from_storage(client: Minio, file_name: str, bucket_name: str):
    response = client.get_object(
        bucket_name=bucket_name,
        object_name=file_name,
    )
    return response
