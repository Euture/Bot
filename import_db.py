import sqlite3
import datetime
import re
import os
from openpyxl import load_workbook
from config import max_lessons


class DataBase(object):
    connection = None
    cursor = None

    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    friday = 'Пятница'
    saturday = 'Суббота'
    week = [monday, tuesday, wednesday, friday, saturday]

    regex_class = None
    regex_empty = None

    def __init__(self, clean=False, check_same_thread=True):
        if clean and 'DB.sqlite' in os.listdir():
            os.remove('DB.sqlite')
        self.connection = sqlite3.connect('DB.sqlite', check_same_thread=check_same_thread)
        self.cursor = self.connection.cursor()
        self.regex_class = re.compile(r'\d{1,2} "\w\"')
        self.regex_empty = re.compile(r'\s{2,}')
        if clean:
            self.cursor.execute('''CREATE TABLE class
                                            (
                                                id INTEGER PRIMARY KEY, 
                                                number INTEGER,
                                                postfix TEXT
                                            )
                                 ''')
            self.cursor.execute('''CREATE TABLE lesson
                                            (
                                                id INTEGER PRIMARY KEY, 
                                                day TEXT, 
                                                text TEXT, 
                                                class_id INTEGER, 
                                                FOREIGN KEY(class_id) REFERENCES class(id)
                                            )
                                ''')
            self.cursor.execute('''CREATE TABLE user
                                          (
                                              id INTEGER PRIMARY KEY, 
                                              class_id INTEGER, 
                                              FOREIGN KEY(class_id) REFERENCES class(id)
                                          )
                              ''')

    def close(self):
        self.connection.commit()
        self.connection.close()

    def __delete__(self, instance):
        self.connection.close()

    def string_filter(self, value):
        return re.sub(self.regex_empty, '\n', value)

    def get_classes(self):
        self.cursor.fetchall()
        self.cursor.execute('Select * FROM class')
        return self.cursor.fetchall()

    def get_last_class(self):
        self.cursor.fetchall()
        self.cursor.execute('Select * FROM class')
        return self.cursor.fetchall().pop()

    def save_class(self, value):
        number, postfix = value.split(' ')
        self.cursor.execute(f"INSERT INTO class(number, postfix) VALUES ('{number}','{postfix}')")

    def save_lesson(self, value, day):
        class_ = self.get_last_class()
        value = self.string_filter(value)
        self.cursor.execute(f"INSERT INTO lesson(day, text, class_id) VALUES ('{day}', '{value}', '{class_[0]}')")

    def get_user(self, id):
        a = self.cursor.fetchall()
        self.cursor.execute(f'Select * FROM user WHERE id={id}')
        return self.cursor.fetchall()

    def save_user(self, id, class_tuple):
        if not self.get_user(id):
            print('Сохраняем')
            self.cursor.execute(f"INSERT INTO user(id, class_id) VALUES ('{id}', '{class_tuple[0]}')")
            # сохраняем тк использует только бот функцию
            self.connection.commit()

    def get_all_users(self):
        self.cursor.fetchall()
        self.cursor.execute('Select * FROM user')
        return self.cursor.fetchall()

    def get_day_at_class(self, class_tuple, day=monday):
        self.cursor.execute('''Select * FROM lesson WHERE day='%s' AND class_id='%s' ''' % (day, class_tuple[0]))
        return self.cursor.fetchall()

    def import_timetable(self):
        regex = re.compile(r'.xls')
        files = list(filter(regex.search, os.listdir()))
        if files:
            file = files[0]
            wb = load_workbook(file)
            sheet = wb.active

            for col in sheet.columns:
                read_days = False
                lesson_count = 0
                for cell in col:
                    value = cell.value
                    # записываем уроки
                    if read_days:
                        if value:
                            self.save_lesson(value=value, day=self.week[int(lesson_count / max_lessons)])
                        lesson_count += 1
                    else:
                        if value:
                            find_class = self.regex_class.search(str(value))
                            # записываем класс
                            if find_class:
                                self.save_class(value=find_class.string)
                                read_days = True
            self.connection.commit()
        else:
            print("Нет xls файла")


db = DataBase(clean=True)
db.import_timetable()
