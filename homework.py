import logging
import os
import time

import telegram
import requests
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
    filename='program.log',
    level=logging.DEBUG,
    filemode='a')


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logging.info(
        f'Отправлено сообщение с обновленным статусом. "{message}"')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        if homework_statuses.status_code == 200:
            response = homework_statuses.json()
            logging.debug('Ответ от сервера, на запрос API, получен.')
            return response
        else:
            logging.error('Не пришел ответ от эндпоинта.')
            raise Exception
    except Exception:
        logging.error('Проблемы с доступом к эндпоинту.')
        raise Exception('Увы. Произошла ошибка при запросе к серверу.')


def check_response(response):
    if type(response) is not dict:
        raise TypeError(
            'В ответ от эндпоинта пришел не словарь.')
    elif ('homeworks') not in response:
        logging.error('Отсутствует ключ homeworks.')
        raise IndexError(
            'Отсутствует ключ homeworks.')
    elif len(response['homeworks']) == 0:
        raise ValueError(
            'Пришел пустой список домашней работы.')
    elif ('homeworks') not in response:
        raise IndexError(
            'Отсутствует ключ homeworks.')
    elif ('current_date') not in response:
        raise IndexError(
            'Отсутствует ключ current_date.')
    elif type(response['homeworks']) is not list:
        raise TypeError(
            'Данные по домашней работе пришли не списком.')
    else:
        return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения,
        которые необходимы для работы программы."""
    token_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if None in token_list:
        logging.critical('Ошибка при запросе к основному API.')
        return False

    else:
        logging.debug('Проверка переменных окружения пройдена.')
        return True


def main():
    """Основная логика работы бота."""
    PREVIOUS_STATUS = ''
    current_timestamp = int(time.time())
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    else:
        raise SystemExit('Не удалось найти один из Token')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) != 0:
                homework = homeworks[0]
                current_status = homework['status']
                if current_status != PREVIOUS_STATUS:
                    logging.info(
                        'Найден обновленный статус по домашней работе.')
                    PREVIOUS_STATUS = homework['status']
                    message = parse_status(homework)
                    send_message(bot, message)
                    current_timestamp = response['current_date']
                else:
                    logging.debug(
                        'Статус о работе собран из API, но обновлений нет.')
                    time.sleep(RETRY_TIME)
            else:
                logging.debug(
                    'Нет работ, которые вы бы могли отслеживать.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
