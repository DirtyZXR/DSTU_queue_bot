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
        self.markup_queue = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        self.hideKeyboard = types.ReplyKeyboardRemove()
        self.lesson_started = False
        self.now_lesson = None
        # self.gruop_id = -1852603965
        self.gruop_id = -514977824
        self.wait_exhacnge = {}
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

        @self.bot.message_handler(commands=['add'])
        def main(message):
            cid = message.from_user.id
            group = message.chat.id
            if cid == self.sid_admin:
                name_lesson = self.bot.reply_to(message, text='Напиши название пары для создания на неё очереди.')
                self.bot.register_next_step_handler(name_lesson, add_lesson_quque)
            else:
                self.bot.send_message(group, text='Добавить очередь может только администатор')

        @self.bot.message_handler(commands=['check'])
        def check(message):
            if message.chat.type == 'private':
                lesson = message.text.strip()
                lesson = lesson.split(' ')
                if len(lesson) == 1:
                    lesson = self.bot.send_message(message.chat.id, text='Выбери пару', reply_markup=self.markup_queue)
                    self.bot.register_next_step_handler(lesson, check_private)
                elif len(lesson) == 2:
                    lesson = lesson[1]
                    if lesson in self.all_quque:
                        list_quque = get_quque(lesson)
                        self.bot.send_message(message.chat.id, text=list_quque, reply_markup=self.hideKeyboard)
                    else:
                        self.bot.send_message(message.chat.id, text='Пара не найдена.', reply_markup=self.hideKeyboard)
                else:
                    self.bot.reply_to(message, text='Пара не найдена. Отправь команду в формате \n/check Название пары', reply_markup=self.hideKeyboard)
            else:
                lesson = message.text.strip()
                lesson = lesson.split(' ')
                if len(lesson) == 2:
                    lesson = lesson[1]
                    if lesson in self.all_quque:
                        list_quque = get_quque(lesson)
                        self.bot.send_message(message.chat.id, text=list_quque, reply_markup=self.hideKeyboard)
                    else:
                        self.bot.reply_to(message,
                                          text='Пара не найдена. Отправь команду в формате \n/check Название пары', reply_markup=self.hideKeyboard)
                else:
                    self.bot.reply_to(message, text='Пара не найдена. Отправь команду в формате \n/check Название пары', reply_markup=self.hideKeyboard)

        @self.bot.message_handler(commands=['delete'])
        def delete(message):
            cid = message.from_user.id
            group = message.chat.id
            if cid == self.sid_admin:
                name_lesson = self.bot.reply_to(message, text='Выбери название пары для удаления на неё очереди.',
                                                reply_markup=self.markup_queue)
                self.bot.register_next_step_handler(name_lesson, delete_quque)
            else:
                self.bot.send_message(group, text='Удалить очередь может только администатор')

        @self.bot.message_handler(commands=['start_lesson'])
        def start(message):
            if message.from_user.id == self.sid_admin:
                lesson = message.text
                lesson = lesson.split(' ')
                if len(lesson) == 2:
                    lesson = lesson[1]
                    if lesson in self.all_quque:
                        list_quque = get_quque(lesson)
                        self.now_lesson = lesson
                        self.bot.send_message(self.gruop_id
                                              , text=f'Очередь начата.\n\n{list_quque}\nДля  проруска')
                        self.lesson_started = True


                    else:
                        self.bot.reply_to(message,
                                          text='Пара не найдена. Отправь команду в формате \n/start_lesson Название пары')
                else:
                    self.bot.reply_to(message,
                                      text='Пара не найдена. Отправь команду в формате \n/start_lesson Название пары')
            else:
                self.bot.send_message(message.chat.id, text='Начать очередь может только администатор')

        @self.bot.message_handler(commands=['skip', 'next'])
        def start_lesson(message):
            if self.lesson_started:
                students_now = self.all_quque[self.now_lesson]
                next_s = list(students_now.keys())[0]
                if message.from_user.id == self.sid_admin or message.from_user.id == self.students[next_s]:
                    print(message.text)
                    if message.text == '/next':
                        for student in self.all_quque[self.now_lesson]:
                            self.all_quque[self.now_lesson][student] -= 1
                            if self.all_quque[self.now_lesson][student] <= 0:
                                self.all_quque[self.now_lesson][student] = 24

                        sorted_dict = {k: v for k, v in
                                       sorted(self.all_quque[self.now_lesson].items(), key=lambda item: item[1])}
                        self.all_quque[self.now_lesson] = sorted_dict
                        students_now = self.all_quque[self.now_lesson]
                        next_s = list(students_now.keys())[0]
                        self.bot.send_message(message.chat.id, text=f'Следующий {next_s}')
                    else:
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
                                    self.all_quque[self.now_lesson][
                                        list(self.all_quque[self.now_lesson].keys())[i + 1]] -= 1
                                self.all_quque[self.now_lesson][next_s] = skiped + 1

                                sorted_dict = {k: v for k, v in sorted(self.all_quque[self.now_lesson].items(),
                                                                       key=lambda item: item[1])}
                                self.all_quque[self.now_lesson] = sorted_dict
                                students_now = self.all_quque[self.now_lesson]
                                next_s = list(students_now.keys())[0]
                                next_s_1 = list(students_now.keys())[1]
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
                self.bot.reply_to(message, text='Эту команду можно использовать только во время начавшейся пары.')

        @self.bot.message_handler(commands=['stop_lesson'])
        def stop_lesson(message):
            if message.from_user.id == self.sid_admin:
                self.lesson_started = False
                self.now_lesson = None
                self.bot.send_message(self.gruop_id
                                      , text=f'Пара закончена.')
            else:
                self.bot.send_message(message.chat.id, text='Закончить пару может только администатор')

        @self.bot.message_handler(commands=['list_lessons'])
        def list_lessons(message):
            list_lessons = ''
            for lesson in self.all_quque:
                list_lessons += lesson + '\n'
            self.bot.send_message(message.chat.id, text=f'Список пар:\n{list_lessons}')

        @self.bot.message_handler(commands=['edit_students'])
        def del_add__list_stud(message):
            pass

        @self.bot.message_handler(commands=['save'])
        def save(message):
            pass

        @self.bot.message_handler(commands=['exchange'])
        def exchange(message):
            if message.chat.type == 'private':
                cid = message.from_user.id
                lesson = self.bot.send_message(message.chat.id, text='Выбери пару, на которой ты хочешь поменяться.',
                                               reply_markup=self.markup_queue)
                self.bot.register_next_step_handler(lesson, exchange_quque)
            else:
                self.bot.reply_to(message, text=f'Эту команду можно использовать только в личных сообщениях.')

        def exchange_quque(message):
            lesson = message.text
            if lesson in self.all_quque:
                stud = self.bot.send_message(message.chat.id, text="Выбери, с кем хочешь поменяться",
                                             reply_markup=self.markup_students)
                self.bot.register_next_step_handler(stud, request_exchange, lesson)



            else:
                self.bot.send_message(message.chat.id, text='Пара не найдена.')

        def request_exchange(message, lesson):
            stud = message.text
            self.bot.send_message(message.chat.id, text=f'Отправил запрос {stud.text} на смену. Ожидайте подтвержения.', reply_markup=self.hideKeyboard)
            items = self.students.items()
            result = next((item for item in items if item[1] == message.from_user.id), None)
            result = result[0]
            if self.students[stud] in self.wait_exhacnge:
                self.wait_exhacnge[self.students[stud]].append(
                    [(self.students[result], lesson), None])
            else:
                items = self.students.items()
                result = next((item for item in items if item[1] == message.from_user.id), None)
                result = result[0]
                self.wait_exhacnge[self.students[stud]] = [[(self.students[result], lesson), None]]
            items = list(self.students.items())
            result = next((item for item in items if item[1] == message.from_user.id), None)
            result = result[0]
            self.bot.send_message(self.students[stud],
                                  text=f"{result} просит вас поменятся местами на паре {lesson}."
                                       f"\nЕсли вы согласны отправте /yes, в противном случае /no")

        @self.bot.message_handler(commands=['yes', 'no'])
        def wait_answer(message):
            if message.from_user.id in self.wait_exhacnge:
                if len(self.wait_exhacnge[message.from_user.id]) != 1:
                    self.wait_exhacnge[message.from_user.id].reverse()

                for i in range(len(self.wait_exhacnge)):
                    if message.text == '/yes':
                        self.wait_exhacnge[message.from_user.id][i][1] = True
                        stud1, lesson = self.wait_exhacnge[message.from_user.id][i][0]
                        stud2 = message.from_user.id

                        items = list(self.students.items())
                        stud1 = next((item for item in items if item[1] == stud1), None)
                        stud2 = next((item for item in items if item[1] == stud2), None)
                        stud1, stud2 = stud1[0], stud2[0]

                        self.all_quque[lesson][stud1[0]], self.all_quque[lesson][stud2[0]] = \
                            self.all_quque[lesson][stud2[0]], self.all_quque[lesson][stud1[0]]

                        sorted_dict = {k: v for k, v in
                                       sorted(self.all_quque[lesson].items(), key=lambda item: item[1])}
                        self.all_quque[lesson] = sorted_dict

                        self.bot.send_message(self.wait_exhacnge[message.from_user.id][i][0][0],
                                              text=f'{stud2} подтвердил ваш запрос'
                                                   f'на смену на паре {lesson}.')

                        self.wait_exhacnge[message.from_user.id].pop(i)

                        self.bot.send_message(message.chat.id, text=f'Запрос от {stud1} подтверждён.')

                    else:
                        self.wait_exhacnge[message.from_user.id][i][1] = False
                        stud1, lesson = self.wait_exhacnge[message.from_user.id][i][0]
                        stud2 = message.from_user.id

                        items = list(self.students.items())
                        stud1 = next((item for item in items if item[1] == stud1), None)
                        stud2 = next((item for item in items if item[1] == stud2), None)
                        print(stud2)
                        stud1, stud2 = stud1[0], stud2[0]

                        self.bot.send_message(self.wait_exhacnge[message.from_user.id][i][0][0],
                                              text=f'{stud2} отклонил ваш запрос')

                        self.wait_exhacnge[message.from_user.id].pop(i)

                        self.bot.send_message(message.chat.id, text=f'Запрос от {stud1} отклонён.')

                self.wait_exhacnge.pop(message.from_user.id)
            else:
                self.bot.send_message(message.chat.id, text='У вас нет запросов на смену.')

        def delete_quque(message):
            del_check = self.markup_queue.keyboard.copy()
            for i in range(len(del_check)):
                del_ready = del_check[i][0]['text']
                if del_ready == message.text:
                    self.markup_queue.keyboard.pop(i)

            self.all_quque.pop(message.text)
            self.bot.send_message(message.chat.id, text=f'Очередь на пару {message.text} удалена.',
                                  reply_markup=self.hideKeyboard)

        def check_private(message):
            lesson = message.text
            if lesson in self.all_quque:
                list_quque = get_quque(lesson)
                self.bot.send_message(message.chat.id, text=list_quque, reply_markup=self.hideKeyboard)
            else:
                self.bot.send_message(message.chat.id,
                                      text='Пара не найдена. Используй команду заново и выбери пару из предложенных')

        def get_quque(message_text):
            lesson = message_text
            lesson = self.all_quque[lesson]

            print(lesson)
            list_queue = ''
            for student in lesson:
                list_queue += str(lesson[student]) + ' --- ' + student + '\n'

            return list_queue

        def add_lesson_quque(message):  # todo сделать добавление очереди

            self.all_quque[message.text] = self.students.copy()
            lesson_quque = self.all_quque[message.text]
            i = 1
            for student in lesson_quque:
                lesson_quque[student] = i
                i += 1

            self.bot.send_message(message.chat.id, text='Очередь создана.')
            print(self.all_quque)
            self.markup_queue.add(types.KeyboardButton(message.text))

    def run(self):
        asyncio.run(self.bot.polling())


g = TGbot()
g.run()

# self.all_quque[self.now_lesson][list(self.all_quque[self.now_lesson].keys())[0]], \
#     self.all_quque[self.now_lesson][list(self.all_quque[self.now_lesson].keys())[1]] = \
#     self.all_quque[self.now_lesson][list(self.all_quque[self.now_lesson].keys())[1]], \
#         self.all_quque[self.now_lesson][list(self.all_quque[self.now_lesson].keys())[0]]
