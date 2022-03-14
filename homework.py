import logging
import os
import time
import sys
from http import HTTPStatus

import telegram
import requests
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


filename = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'bot.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(filename=filename)
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Отправлено сообщение с обновленным статусом: {message}.')
        return True
    except Exception as error:
        logger.error(
            f'Сообщение не отправлено из за ошибки: {error}.')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        if homework_statuses.status_code == HTTPStatus.OK:
            response = homework_statuses.json()
            logger.debug('Ответ от сервера на запрос API получен.')
            return response
        else:
            logger.error('Не пришел ответ от эндпоинта.')
            raise Exception
    except Exception:
        logger.error('Проблемы с доступом к эндпоинту.')
        raise Exception('Увы. Произошла ошибка при запросе к серверу.')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError(
            'В ответ от эндпоинта пришел не словарь.')
    elif ('homeworks') not in response:
        logger.error('Отсутствует ключ homeworks.')
        raise IndexError(
            'Отсутствует ключ homeworks.')
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
    """Извлекает из информации о конкретной.
    домашней работе статус работы.
    """
    homework_name = homework['homework_name']
    if 'homework_name' not in homework:
        logger.error('В ответе API нет ключа homework_name.')
        raise KeyError('В ответе API нет ключа homework_name.')
    homework_status = homework['status']
    if 'status' not in homework:
        logger.error('В ответе API нет ключа status.')
        raise KeyError('В ответе API нет ключа status.')
    if homework_status not in HOMEWORK_STATUSES.keys():
        message_home_status = (
            f'Статус домашней работы {homework_status} некорректен.'
        )
        logger.error(message_home_status)
        raise KeyError(message_home_status)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения,.
    которые необходимы для работы программы.
    """
    token_list = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for token, var in token_list.items():
        if var is None:
            logger.critical(
                f'Отсутсвует TOKEN {token}.')
            return False
    else:
        logger.debug('Проверка переменных окружения прошла успешно.')
        return True


def main():
    """Основная логика работы бота."""
    PREVIOUS_STATUS = ''
    current_timestamp = int(time.time())
    if check_tokens():
        try:
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
        except Exception as error:
            message = f'Сбой при инициализации бота: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)
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
                    logger.info(
                        'Найден обновленный статус по домашней работе.')
                    message = parse_status(homework)
                    if send_message(bot, message) == True:
                        PREVIOUS_STATUS = homework['status']
                        current_timestamp = response['current_date']
                else:
                    logger.debug(
                        'Статус о работе собран из API, но обновлений нет.')
                    time.sleep(RETRY_TIME)
            else:
                logger.debug(
                    'Нет работ, которые вы бы могли отслеживать.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
