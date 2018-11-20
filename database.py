import datetime
import re
import os
from openpyxl import load_workbook
from config import max_lessons, project_dir
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

Base = declarative_base()


class Class(Base):
    __tablename__ = 'class'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    postfix = Column(String)

    def __str__(self):
        return f'{self.number} {self.postfix}'

    def __init__(self, number, postfix):
        self.number = number
        self.postfix = postfix


class Lesson(Base):
    __tablename__ = 'lesson'

    id = Column(Integer, primary_key=True)
    _class = Column(ForeignKey('class.id'))
    number = Column(Integer)
    text = Column(String)
    day = Column(String)

    def __str__(self):
        return f'📌{self.number} урок\n{self.text}\n\n'

    def __init__(self, class_id, number, text, day):
        self._class = class_id
        self.number = number
        self.text = text
        self.day = day


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True)
    _class = Column(ForeignKey('class.id'))

    def __str__(self):
        return f'ID={self.id} Class={self._class}'

    def __init__(self, id, class_id):
        self.id = id
        self._class = class_id


class DataBase(object):
    engine = None
    session = None
    connect = None
    meta = MetaData()

    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    thursday = 'Четверг'
    friday = 'Пятница'
    saturday = 'Суббота'
    sunday = 'Воскресенье'
    week = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]

    regex_class = None
    regex_empty = None

    def __init__(self, clean=False, echo=False):
        if clean and 'DB.sqlite' in os.listdir():
            os.remove('DB.sqlite')
        self.engine = create_engine(f'sqlite:///{project_dir}\\DB.sqlite', echo=echo)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        if clean:
            Base.metadata.create_all(self.engine)

        self.regex_class = re.compile(r'\d{1,2} "\w\"')
        self.regex_empty = re.compile(r'\s{2,}')

    def get_user(self, id):
        return self.session.query(User).filter_by(id=id).first()

    def get_class(self, id):
        return self.session.query(Class).filter_by(id=id).first()

    def save_user(self, id, class_id):
        if not self.get_user(id):
            self.session.add(User(id=id, class_id=class_id))
            self.session.commit()

    def delete_user(self, id):
        user = self.get_user(id)
        self.session.delete(user)

    def get_all_users(self):
        return list(self.session.query(User).all())

    def get_day_at_class(self, user_id, day=monday):
        user = self.get_user(id=user_id)
        result = f'📅 {day}\n\n'
        lesssons = self.session.query(Lesson).filter(Lesson._class == user._class, Lesson.day == day)
        for lesson in lesssons:
            result += str(lesson)
        return result

    def close(self):
        self.session.close()

    def string_filter(self, value):
        return re.sub(self.regex_empty, '\n', value)

    def get_classes(self):
        return self.session.query(Class).all()

    def get_last_class(self):
        return self.session.query(Class).all().pop()

    def save_class(self, value):
        number, postfix = value.split(' ')
        self.session.add(Class(number=int(number), postfix=postfix))
        self.session.commit()

    def save_lesson(self, number, value, day):
        _class = self.get_last_class()
        value = self.string_filter(value)
        self.session.add(Lesson(class_id=_class.id, number=number, text=value, day=day))

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
                            self.save_lesson(number=(lesson_count % max_lessons) + 1, value=value,
                                             day=self.week[int(lesson_count / max_lessons)])
                        lesson_count += 1
                    else:
                        if value:
                            find_class = self.regex_class.search(str(value))
                            # записываем класс
                            if find_class:
                                self.save_class(value=find_class.string)
                                print(f'Класс {value} найден')
                                read_days = True
            self.session.commit()
        else:
            print("Нет xls файла")
