import telebot
from telebot import apihelper
import time
import subprocess
import config
from import_db import DataBase


tor = subprocess.Popen('start_tor.bat')
time.sleep(10)
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:9050'
}
bot = telebot.TeleBot(config.token)
db = DataBase(check_same_thread=False)

# Обработчик команд '/start'
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, str(db.get_all_users()))
    db.save_user(id=message.from_user.id, class_tuple=db.get_last_class())
    bot.send_message(message.chat.id, str(db.get_all_users()))


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

tor.kill()
while 1:
    if not db.connection.in_transaction:
        db.close()
        continue