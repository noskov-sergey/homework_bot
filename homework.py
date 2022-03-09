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
    params = {'from_date': 1644457054}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return homework_statuses.json()


def check_response(response):
    homeworks = response['homeworks']
    return homeworks
    ...


def parse_status(homework):
    homework_name = ...
    homework_status = ...

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения,
        которые необходимы для работы программы."""
    token_list = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    if None or '' in token_list:
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    check_tokens()

    while True:
        print('lol')
        try:
            response = get_api_answer(current_timestamp)
            pprint(response)
            print(check_response(response))
            ...

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

print(check_tokens)
