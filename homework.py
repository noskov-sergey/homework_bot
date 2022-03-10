import logging
import os
import time
from pprint import pprint

from telegram import Bot
import telegram
import requests
from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': 1644458933}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        return homework_statuses.json()
    except Exception:
        raise Exception('Увы. Произошла ошибка при запросе к серверу.')


def check_response(response):
    if type(response) is not dict:
        raise TypeError(
            'Увы. не работает. В ответ на запрос должен прийти словарь')
    elif type(response['homeworks']) is not list:
        raise TypeError(
            'Увы, не работает. Домашняя работата должна передавать список')
    elif ('homeworks') not in response:
        raise IndexError(
            'Увы, не работает. Домашней работы нет в переданных данных')
    else:
        return response['homeworks'][0]


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    ...

    verdict = HOMEWORK_STATUSES[homework_status]

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения,
        которые необходимы для работы программы."""
    token_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if None in token_list:
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    print(check_tokens())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            lol = parse_status(homework)
            current_timestamp = ...
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
