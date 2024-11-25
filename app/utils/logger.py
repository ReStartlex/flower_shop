import logging
from logging.handlers import RotatingFileHandler

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
