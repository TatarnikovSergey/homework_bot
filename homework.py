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
    bot.send_message(TELEGRAM_CHAT_ID, message)


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
    """Проверка наличия в ответе API ключей имени и статуса домашней работы"""
    if response['homeworks']:
        homework = response['homeworks'][0]
        if homework['homework_name'] and homework['status']:
            return homework


def parse_status(homework):
    """Подготовка информации о статусе домашней работы"""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    print(f'Изменился статус проверки работы "{homework_name}". {verdict}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    current_work = {}
    current_status = ''


    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time())
    timestamp = 1714100000

#     ...

    while True:
        try:
            # breakpoint()
            response = get_api_answer(timestamp)
            pprint(current_work)
            if response['homeworks']:
                last_work = check_response(response)
                if last_work != current_work:
                    current_work = last_work

                pprint(last_work)
                pprint(current_work)
            # if last_work and last_work['status'] != current_status:
            #     current_status = last_work['status']
            #     pprint(current_status)
            #     send_message(bot, parse_status(last_work))
            if current_work and current_work['status'] != current_status:
                current_status = current_work['status']
                pprint(current_status)
                send_message(bot, parse_status(current_work))

                # if not work_status:
                #     work_status = last_work
                #     pprint(work_status)
                #     send_message(bot, parse_status(last_work))
                #     # timestamp = list_work['current_date']
                #     # pprint(timestamp)
                #     # breakpoint()
                # else:
                #     if last_work == work_status:
                #         pass
                #     else:
                #         work_status = last_work
                #         send_message(bot, parse_status(last_work))


        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        timestamp = int(time.time())
        time.sleep(10)
        current_work = {
            'date_updated': '2024-05-05T14:55:44Z',
            'homework_name': 'TatarnikovSergey!!!!!!!!!!!!!!!!!2.zip',
            'id': 1213607,
            'lesson_name': 'Финальный проект спринта: Vice Versa',
            'reviewer_comment': 'Супер! Принято!) ',
            'status': 'approved'
        }

if __name__ == '__main__':
    main()


# get_api_answer(1714100000)
# get_api_answer(timestamp)
