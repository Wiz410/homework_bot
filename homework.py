import os
import sys
import time
import logging
from logging import StreamHandler
from http import HTTPStatus

import telegram
from telegram import Bot
import requests
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: int = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: str = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[StreamHandler(sys.stdout)],
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def check_tokens() -> None:
    """Проверка начилия переменных окружения.

    Проверка наличия необходимых для работы бота
    переменных окружения в файле .env.
    """
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    )
    for token in tokens:
        message = f'Отсутствует обязательная переменная окружения: {token}.'
        if token is None:
            logging.critical(message)
            raise ValueError(message)
    logging.debug('Переменные окружения доступны.')


def send_message(bot: Bot, message: str) -> None:
    """Отправка сообщения пользователю.

    Args:
        bot (telegram.Bot): Экземпляр Bot.
        message (str): Подготовленное сообщение.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Бот отправил сообщение "{message}"')
    except Exception:
        logging.error('Боту не удалось отправить сообщение!')


def get_api_answer(timestamp: int) -> dict:
    """Запрос для получения данный от API Practicum.

    Args:
        timestamp (int): Время в формате Unix time.

    Returns:
        response (dict): Ответ API приведенный к типу данных: словарь.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.error(error)
    if response.status_code != HTTPStatus.OK:
        message: str = (
            f'Данные от API не получены, '
            f'ответ сервера: {response.status_code}'
        )
        logging.error(message)
        raise Exception(message)
    else:
        logging.debug('Ответ от API получен.')
        return response.json()


def check_response(response: dict) -> dict:
    """Проверка ответа от API Practicum.

    Args:
        response (dict): Ответ API.

    Returns:
        response (dict): Если в ответе API список homeworks пустой
            ответ вернется без изменений.
        homeworks (dict): Иначе словарь из списка homeworks
    """
    if type(response) != dict:
        logging.error(
            f'Полученные данные отличаются от словаря (dict) '
            f'тип данных: {type(response)}!'
        )
        raise TypeError(
            f'Ответ от API пришел в виде {type(response)}'
        )
    for key in 'current_date', 'homeworks':
        if response.get(key) is None:
            message: str = f'В ответе нет нужного ключа: {key}'
            logging.error(message)
            raise KeyError(message)
    key_homeworks: str = 'homeworks'
    if type(response.get(key_homeworks)) != list:
        message: str = f'{key_homeworks} не содержит список.'
        logging.error(message)
        raise TypeError(message)
    elif len(response.get(key_homeworks)) == 0:
        logging.debug('Ответ от API проверен, нет новых данных.')
        return response
    else:
        logging.debug('Ответ от API проверен.')
        homeworks: list = response.get(key_homeworks)
        return homeworks[0]


def parse_status(homework: dict) -> str:
    """Получение информации из ответа.

    Получение информации об имени и статусе работы.
    Подготовка сообщения.

    Args:
        homework (dict): Ответ API или словарь из списка homeworks.
    """
    get_homeworks = homework.get('homeworks')
    if get_homeworks is not None and len(get_homeworks) == 0:
        message: str = 'Нет новых статусов о работе.'
        logging.debug(message)
        return message
    for key in 'homework_name', 'status':
        if key not in homework:
            message: str = f'В ответе API нет ключа: {key}.'
            logging.error(message)
            raise KeyError(message)
    key_status: str = 'status'
    if homework[key_status] not in HOMEWORK_VERDICTS:
        message: str = f'Значение ключа: {key_status} недокументированное.'
        logging.error(message)
        raise KeyError(message)
    else:
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS[homework[key_status]]
        logging.debug('Сообщение подготовлено.')
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота.

    Note:
        Вызов функций:
            Проверка переменных.
            Отправка запроса к API.
            Проверка ответа от API.
            Подготовка сообщения.
            Отправка сообщения.
        Повторение через 10 минут.
    """
    check_tokens()
    bot: Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp: int = int(time.time())
    last_time: bool or int = None
    last_message: str = ''
    last_error: str = ''
    while True:
        try:
            if last_time is not None:
                response = get_api_answer(last_time)
            else:
                response = get_api_answer(timestamp)
            last_time = response.get('current_date')
            homework = check_response(response)
            message = parse_status(homework)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != last_error:
                send_message(bot, message)
                last_error = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
