import telebot
from telebot import apihelper
import time
import subprocess
import config
from database import DataBase

tor = subprocess.Popen('start_tor.bat')
time.sleep(10)
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:9050'
}
bot = telebot.TeleBot(config.token)
db = DataBase(echo=True)


# Обработчик команд '/start'
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, db.get_all_users() or 'Пусто')
    db.save_user(id=message.from_user.id, _class=db.get_last_class())
    bot.send_message(message.chat.id, db.get_all_users() or 'Пусто')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_msg(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    if tor:
        while 1:
            try:
                bot.polling(none_stop=True)
            except Exception:
                pass
