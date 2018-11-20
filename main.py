import telebot
from telebot import apihelper
import time
import subprocess
import config
from database import DataBase
from menu import Menu

tor = subprocess.Popen('start_tor.bat')
time.sleep(10)
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:9050'
}
bot = telebot.TeleBot(config.token)
db = DataBase(echo=True)
menu = Menu()

# Обработчик команд '/start'
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    #if not db.get_user(id=message.from_user.id):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!' + '\n' + 'Выбери класс',
                     reply_markup=menu.classes_markup)
    #db.save_user(id=message.from_user.id, _class=1)


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
