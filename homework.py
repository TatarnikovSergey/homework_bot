import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
from dotenv import load_dotenv
from telebot import TeleBot, apihelper

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

PRACTICUM_TOKEN: str = os.getenv('P_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('T_TOKEN')
TELEGRAM_CHAT_ID: str = os.getenv('T_CHAT_ID')

RETRY_PERIOD = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности секретных ключей."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправка сообщения телеграмм ботом."""
    logger.debug(f'Отправляем сообщение {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправлено сообщение {message}')
    except apihelper.ApiException as error:
        logger.error(f'Ошибка {error} отправки сообщения {message} ')


def get_api_answer(timestamp):
    """Запрос к API."""
    try:
        response = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        logger.error(f'Ошибка {error} запроса к API')
        raise ConnectionError
    if response.status_code != HTTPStatus.OK:
        logger.error(f'Ошибка {response.status_code} при запросе к API')
        raise ConnectionError
    return response.json()


def check_response(response):
    """Проверка наличия в ответе API ключей имени и статуса домашней работы."""
    try:
        if not (isinstance(response, dict)
                and isinstance(response['homeworks'], list)):
            raise TypeError(
                logger.error('Ответ API не соответствует документации')
            )
        elif not response['homeworks']:
            logger.debug('Список домашних работ пуст')
        else:
            homework = response['homeworks'][0]
            if homework['homework_name'] and homework['status']:
                return homework
    except KeyError:
        raise logger.error('В ответе API отсутствуют необходимые данные')


def parse_status(homework):
    """Подготовка информации о статусе домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        raise logger.error('Ответ API не соответствует документации')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Invalid tokens')
        sys.exit()
    current_work = {}
    current_status = ''
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework != current_work:
                current_work = homework
            if current_work and current_work['status'] != current_status:
                current_status = current_work['status']
                logger.debug('Изменился статус домашней работы')
                send_message(bot, parse_status(current_work))
                timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
