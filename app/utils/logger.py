import logging
from logging.handlers import RotatingFileHandler
from flask import current_app

def setup_logger():
    # Создаём логгер
    logger = logging.getLogger('flower_shop')
    logger.setLevel(logging.DEBUG)

    # Форматирование логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Хендлер для записи в файл с ротацией
    file_handler = RotatingFileHandler(
        'logs/flower_shop.log', maxBytes=1000000, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def log_to_redis(level, message):
    redis_client = current_app.redis_client
    log_message = f"{level.upper()} - {message}"  # Форматирование сообщения с уровнем логирования
    log_key = f"log:{level}"
    redis_client.lpush(log_key, log_message)
    redis_client.ltrim(log_key, 0, 99)  # Храним только последние 100 сообщений

