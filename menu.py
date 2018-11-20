from database import DataBase, Class, User, Lesson
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class Menu(object):

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