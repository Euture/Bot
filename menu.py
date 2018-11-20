from database import DataBase
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime


class Menu(object):
    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    thursday = 'Четверг'
    friday = 'Пятница'
    saturday = 'Суббота'
    sunday = 'Воскресенье'
    week = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]

    @property
    def classes_markup(self):
        db = DataBase()
        all_classes = db.get_classes()
        buttons = []
        for _class in all_classes:
            button = InlineKeyboardButton(text=str(_class),
                                          callback_data='Class.' + str(_class.id))
            buttons.append(button)
        menu = InlineKeyboardMarkup()
        menu.add(*buttons)
        return menu

    @property
    def week_markup(self):
        week_day = self.week[datetime.datetime.now().weekday()]
        menu = InlineKeyboardMarkup()
        buttons = []
        for day in self.week:
            if not day == self.sunday:
                if not day == week_day:
                    button = InlineKeyboardButton(text=day,
                                                  callback_data='Day.' + str(self.week.index(day)))
                else:
                    button = InlineKeyboardButton(text=day + ' (Сегодня)',
                                                  callback_data='Day.' + str(self.week.index(day)))
                buttons.append(button)
        menu.add(*buttons)
        return menu
