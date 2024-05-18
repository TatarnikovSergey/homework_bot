import os
import time
from pprint import pprint

import requests
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('P_TOKEN')
TELEGRAM_TOKEN = os.getenv('T_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('T_CHAT_ID')

RETRY_PERIOD = 600
timestamp = 0
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    pass


def send_message(bot, message):
    pass


def get_api_answer(timestamp):
    response = requests.get(
        url=ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )
    response = response.json()
    # check_response(response)
    return response


def check_response(response):
    homework = response['homeworks'][0]
    # parse_status(homework)
    return homework

def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    print(f'Изменился статус проверки работы "{homework_name}". {verdict}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    work_status = {}
    response = get_api_answer(timestamp)
    last_work = check_response(response)
    if not work_status:
        work_status.update(last_work)
    else:
        if last_work in work_status:
            pass
        else:
            work_status.update(last_work)
            send_message(bot, parse_status(response))

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

#     ...
#
#     while True:
#         try:
#
#             ...
#
#         except Exception as error:
#             message = f'Сбой в работе программы: {error}'
#             ...
#         ...
#
#
# if __name__ == '__main__':
#     main()


# get_api_answer(1714100000)
get_api_answer(timestamp)
