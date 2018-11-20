import telebot
from telebot import apihelper
import time
import subprocess
import config
from database import DataBase
from menu import Menu
import datetime

tor = subprocess.Popen('start_tor.bat')
time.sleep(10)
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:9050'
}
bot = telebot.TeleBot(config.token)
db = DataBase()
menu = Menu()


# Обработчик команд '/start'
@bot.message_handler(commands=['start'])
def handle_start(message):
    if not db.get_user(id=message.from_user.id):
        bot.send_message(
            message.chat.id,
            f'Привет, {message.from_user.first_name}!' + '\n' + 'Выбери класс',
            reply_markup=menu.classes_markup
        )
    else:
        day = db.week[datetime.datetime.now().weekday()]
        bot.send_message(
            message.chat.id,
            text=db.get_day_at_class(user_id=message.from_user.id, day=day),
            reply_markup=menu.week_markup
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if 'Class' in call.data:
            class_id = int(call.data.split('.')[1])
            print(f'Сохраняем id = {call.from_user.id}, класс = {class_id}')
            db.save_user(id=call.from_user.id, class_id=class_id)
            day = db.week[datetime.datetime.now().weekday()]
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=db.get_day_at_class(user_id=call.from_user.id, day=day),
                reply_markup=menu.week_markup
            )
        if not db.get_user(id=call.from_user.id):
            print(f'Нет пользователя {call.from_user.id}, но просит расписание')
            bot.send_message(
                call.message.chat.id,
                f'Привет, {call.from_user.first_name}!' + '\n' + 'Выбери класс',
                reply_markup=menu.classes_markup
            )
        if 'Day' in call.data:
            day = db.week[int(call.data.split('.')[1])]
            print(f'Дали расписание id = {call.from_user.id}, день = {day}')
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=db.get_day_at_class(user_id=call.from_user.id,
                                         day=day),
                reply_markup=menu.week_markup
            )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_msg(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    if tor:
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                print(e)
                time.sleep(5)
tor.kill()
