import telebot
from pybit.inverse_perpetual import HTTP


api_key_test = ''
api_secret_test = ''
bot_token = ''
user_id = 0

session = HTTP("https://api-testnet.bybit.com", api_key=api_key_test,
                    api_secret=api_secret_test)


def telegram_bot(msg):
    try:
        bot = telebot.TeleBot(bot_token)
        bot.send_message(user_id, msg)
    except Exception as err:
        print(f'{err}')


if __name__ == "__main__":
    telegram_bot('hello world!')
