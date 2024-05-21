import logging
import sys
from logging import StreamHandler
import os
import time
from pprint import pprint

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
    """Проверка доступности секретных ключей"""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(tokens):
        logging.critical('Invalid tokens')
        return False
    else:
        return True





def send_message(bot, message):
    """Отправка сообщения телеграмм ботом"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправлено сообщение {message}')
    except Exception as e:
        logging.error(f'Ошибка {e} отправки сообщения {message} ')

def get_api_answer(timestamp):
    """Запрос к API"""
    response = requests.get(
        url=ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )
    response = response.json()
    return response


def check_response(response):
    """Проверка наличия в ответе API ключей имени и статуса домашней работы"""
    try:
        if not response['homeworks']:
            logger.debug('Список домашних работ пуст')
        else:
            homework = response['homeworks'][0]
        # if homework['homework_name'] and homework['status']:
            return homework
    except KeyError:
        raise logger.error('В ответе API нет ключа "homeworks"')


def parse_status(homework):
    """Подготовка информации о статусе домашней работы"""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        raise logger.error('В ответе нет API ключа "homework_name"')





def main():
    """Основная логика работы бота."""
    tokens = check_tokens()
    current_work = {}
    current_status = ''
    last_work = {}
    last_status = ''

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time())
    timestamp = 1714100000

#     ...

    # while True:
    while tokens:
        try:
            # breakpoint()
            response = get_api_answer(timestamp)
            current_work = check_response(response)
            pprint(current_work)
            if response['homeworks']:
                last_work = current_work
                if last_work != current_work:
                    current_work = last_work
            # else:
            #     logger.debug('Список домашних работ пуст')
            # homework = check_response(response)

            # if last_work and last_work['status'] != current_status:
            #     current_status = last_work['status']
            #     pprint(current_status)
            #     send_message(bot, parse_status(last_work))
            if current_work and current_work['status'] != current_status:
                current_status = current_work['status']
                # print(current_status)
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
        #         #         send_message(bot, parse_status(last_work))
        # except TelegramException as e:
        #     message = f'Ошибка в работе Telegram: {e}'
        #     logger.error(message)
        except IndexError:
            message = f'Список домашних работ пуст'
            logger.error(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)


        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()


# get_api_answer(1714100000)
# get_api_answer(timestamp)
