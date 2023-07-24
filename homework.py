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


def check_tokens() -> bool:
    """Проверка начилия переменных окружения.

    Проверка наличия необходимых для работы бота
    переменных окружения в файле .env.

    Returns:
        True (bool): Все переменные доступны.
        False (bool): Все или часть переменных не доступны.
    """
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    )
    return all(tokens)


def send_message(bot: Bot, message: str) -> None:
    """Отправка сообщения пользователю.

    Args:
        bot (telegram.Bot): Экземпляр Bot.
        message (str): Подготовленное сообщение.
    """
    logging.debug('Отправка сообщения.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(
            f'Боту не удалось отправить сообщение! '
            f'Ошибка: {error}.'
        )
    else:
        logging.debug(f'Бот отправил сообщение "{message}"')


def get_api_answer(timestamp: int) -> dict:
    """Запрос для получения данный от API Practicum.

    Args:
        timestamp (int): Время в формате Unix time.

    Returns:
        response (dict): Ответ API приведенный к типу данных: словарь.
    """
    logging.debug('Отправка запроса к API.')
    request_params: dict[str, str or dict[str, int]] = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        response = requests.get(**request_params)
    except Exception as error:
        logging.error(error)
    if response.status_code != HTTPStatus.OK:
        message: str = (
            f'Данные от API не получены. '
            f'Параметры запроса: {request_params}. '
            f'Ответ сервера: {response.text} код: {response.status_code}.'
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
    logging.debug('Проверки ответа API.')
    if isinstance(response, dict) is False:
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
    if isinstance(response.get(key_homeworks), list) is False:
        message: str = f'{key_homeworks} не содержит список.'
        logging.error(message)
        raise TypeError(message)
    elif len(response.get(key_homeworks)) == 0:
        logging.debug(
            'Проверка закончена: в ответ от API, '
            'нет новых домашних работ.'
        )
        return response
    else:
        logging.debug(
            'Проверка закончена: '
            'в ответ от API есть новая домашняя работа.'
        )
        homeworks: list = response.get(key_homeworks)
        return homeworks[0]


def parse_status(homework: dict) -> str:
    """Получение информации из ответа.

    Получение информации об имени и статусе работы.
    Подготовка сообщения.

    Args:
        homework (dict): Ответ API или словарь из списка homeworks.
    """
    logging.debug('Получения информации из ответа.')
    get_homeworks = homework.get('homeworks')
    if get_homeworks is not None and len(get_homeworks) == 0:
        message: str = 'Нет новых домашних работ.'
        logging.debug(message)
        return message
    keys = (
        'status',
        'homework_name',
    )
    for key in keys:
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
    logging.debug('Проверка переменных окружения.')
    if check_tokens() is False:
        message: str = 'Переменные окружения не доступны, бот остановлен.'
        logging.critical(message)
        raise SystemExit(message)
    logging.debug('Проверка закончена: переменные окружения доступны.')
    bot: Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp: int = int(time.time())
    last_time: bool or int = None
    last_message: str = ''
    last_error: str = ''
    last_status: str = ''
    while True:
        try:
            if last_time is not None:
                response = get_api_answer(last_time)
            else:
                response = get_api_answer(timestamp)
            last_time = response.get('current_date')
            homework = check_response(response)
            message = parse_status(homework)
            if 'status' in homework and last_status != homework['status']:
                last_status = homework['status']
                logging.debug('Статус изменился.')
            else:
                logging.debug('Статус не изменился.')
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
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[StreamHandler(sys.stdout)],
        format=(
            '%(asctime)s '
            '[%(funcName)s - %(lineno)d] '
            '[%(levelname)s] '
            '%(message)s'
        ),
    )
    main()
