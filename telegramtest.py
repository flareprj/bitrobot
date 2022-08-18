import telebot
from pybit.inverse_perpetual import HTTP


api_key_test = 'ZWt6V7T3CP5PuyafJr'
api_secret_test = 'urqEwSLZLiXPR0KlNWx2RoX75CCZM5PxgAV0'
bot_token = '5750172310:AAFzA_I7Qpov6rZkRQ75AQD5mQUJ1N7Kh_4'
user_id = 509963083

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
