import telebot
from telebot import types
import asyncio
import json
import snoop


class TGbot:

    def __init__(self):
        self.bot = telebot.TeleBot(token='6902607895:AAHnUydkC3hmYHdBHErldEnAI6bjNH6qTY4')
        # self.sid_admin = 675869713 dasha
        self.sid_admin = 1028552699
        self.sids = {675869713, }
        self.students = {'Безуглов А.В.': 1, 'Бражко П.П.': 1, "Ващенко А.В.": 1, 'Горбатков С.А.': 1, "Гугиев А.": 1,
                         "Зелинский Д.Р.": 1028552699, "Ильинова Е.А.": 1, "Колеухов В.А.": 1, "Кононенко И.Д.": 1,
                         "Кравченко Р.С.": 1, "Круглянина А.Р.": 1, "Кузмин Д.А.": 1, "Курносенко Г.В.": 1,
                         "Лозинский Д.И.": 1,
                         "Маджарян Р.А": 1, "Мелихов А.Н.": 1, "Михно Р.А.": 1, "Рыбалкин А.В.": 1,
                         "Сапуголевцева Д.В.": 675869713,
                         "Старунский Д.А.": 1, "Струков М.А.": 1, "Федченко Г.Г.": 1, "Царев Н.И.": 1,
                         "Чернаявская Е.В.": 1}

        self.all_quque = {}
        self.hideKeyboard = types.ReplyKeyboardRemove()
        self.lesson_started = False
        # self.gruop_id = -1852603965
        self.gruop_id = -514977824
        self.markup_students = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for student in self.students:
            self.markup_students.add(student)

        @self.bot.message_handler(commands=['start'])
        def start_comand(message):
            self.bot.reply_to(message, text=f"Привет, я бот очереди для нашей группы."
                                            f"Исполюзуй команду \n/register (твоя фамилия)\n"
                                            f"пожалуйста свою фамилю пиши с большой буквы.")
            print(message.chat.id)
            # print(group)
            # print(self.sids)

        @self.bot.message_handler(commands=['register'])
        def register(message):
            succes = False
            text_name = message.text.strip()
            text_name = text_name.split(' ')
            if len(text_name) == 2:
                text_name = text_name[1]
                for fullname in self.students:
                    name = fullname.split(' ')[0]
                    if name == text_name:
                        self.sids.add(message.from_user.id)
                        self.students[fullname] = message.from_user.id
                        self.bot.reply_to(message, text=f"Авторизация успешно пройдена.")
                        succes = True
                        print(self.students)

                if not succes:
                    self.bot.reply_to(message, text=f"Фамилия не найдена. Проверьте правильность сообщения. "
                                                    f"Напоминаю, фамилию следует писать с большой буквы")
            else:
                self.bot.reply_to(message, text=f"Исполюзуй команду в формате\n/register (твоя фамилия)")

        # self.bot.register_next_step_handler(passw, authorization)

        @self.bot.message_handler(commands=['start_lesson'])
        def start(message):
            if message.from_user.id == self.sid_admin:
                self.lesson_started = True
                self.students_now = {}
                self.bot.send_message(self.gruop_id, text='Начата быстрая очередь. Для того чтобы встать в очередь '
                                                          'пропиши /add\nЕсли ты сдал, пиши команду /next\nЕсли ты не готов'
                                                          ' и хочешь пропустить людей вперед пропиши команду\n"/skip кол-во людей"')
            else:
                self.bot.send_message(message.chat.id, text='Начать очередь может только администатор')

        @self.bot.message_handler(commands=['add'])
        def fast_quqe(message):
            if self.lesson_started:
                items = list(self.students.items())
                result = next((item for item in items if item[1] == message.from_user.id), None)
                self.students_now[result[0]] = len(self.students_now) + 1
                self.bot.send_message(message.chat.id, text=get_quque())

            else:
                self.bot.reply_to(message, text='Эту команду можно использовать только во время начавшейся пары.')
        @self.bot.message_handler(commands=['skip', 'next'])
        def start_lesson(message):
            if self.lesson_started:
                if len(self.students_now) >= 1:
                    students_now = self.students_now
                    next_s = list(students_now.keys())[0]
                    if message.from_user.id == self.sid_admin or message.from_user.id == self.students[next_s]:
                        print(message.text)
                        if message.text == '/next':
                            for student in self.students_now.copy():
                                self.students_now[student] -= 1
                                if self.students_now[student] <= 0:
                                    self.students_now.pop(student)
                            next_s = list(students_now.keys())[0]

                            self.bot.send_message(message.chat.id, text=f'Следующий {next_s}')
                        else: #todo сделатать для команды fast и проверить будет ли рабоать не становясь 27
                            skiped = message.text
                            skiped = skiped.split(' ')
                            if len(skiped) == 2:
                                skiped = skiped[1]
                                try:
                                    skiped = int(skiped)
                                except:
                                    self.bot.reply_to(message, text='Укажи сколько человек ты пропускаешь. '
                                                                    'Отправь команду в формате \n/skip Кол-во человек')

                                if type(skiped) == int:

                                    for i in range(skiped):
                                        self.students_now[
                                            list(self.students_now.keys())[i + 1]] -= 1
                                    self.students_now[next_s] = skiped + 1 if skiped + 1 <= len(self.students_now) else len(self.students_now)

                                    sorted_dict = {k: v for k, v in sorted(self.students_now.items(),
                                                                           key=lambda item: item[1])}
                                    self.students_now = sorted_dict
                                    students_now = self.students_now
                                    next_s = list(students_now.keys())[0]
                                    self.bot.send_message(message.chat.id, text=f'Сейчас {next_s}')
                                else:
                                    print(type(skiped))
                            else:
                                self.bot.reply_to(message, text='Укажи сколько человек ты пропускаешь. '
                                                                'Отправь команду в формате \n/skip Кол-во человек')
                    else:
                        self.bot.reply_to(message.chat.id,
                                          text='Продолжить очередь может либо стоящий следуюющим в очереди,'
                                               'либо администратор.')
                else:
                    self.bot.send_message(message.chat.id, text='Очередь пуста')
            else:
                self.bot.reply_to(message, text='Эту команду можно использовать только во время начавшейся пары.')

        @self.bot.message_handler(commands=['stop_lesson'])
        def stop_lesson(message):
            if message.from_user.id == self.sid_admin:
                self.lesson_started = False
                self.students_now = {}
                self.bot.send_message(self.gruop_id
                                      , text=f'Пара закончена.')
            else:
                self.bot.send_message(message.chat.id, text='Закончить пару может только администатор')


        @self.bot.message_handler(commands=['save'])
        def save(message):
            pass

        @self.bot.message_handler(commands=['list'])
        def lsit_quque(message):
            if self.lesson_started:
                self.bot.send_message(message.chat.id, text=get_quque())
            else:
                self.bot.send_message(message.chat.id, text='Пара ещё не началась')

        def get_quque():
            lesson = self.students_now

            print(lesson)
            list_queue = ''
            for student in lesson:
                list_queue += str(lesson[student]) + ' --- ' + student + '\n'

            return list_queue

    def run(self):
        asyncio.run(self.bot.polling())

g = TGbot()
g.run()

