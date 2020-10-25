from telebot import types, TeleBot, apihelper
from .models import *
from .default_lang import ru
from .utils import get_message_text
from time import sleep

msg = ru


class StudentLogic:
    """
    Global class Controller with student logic

    methods:
        check_token
        welcome
        main_menu
        studding
        progress
        view_topic
        view_test
        select_answer
        add_open_answer
        pass_test
        message_in_test

    steps:
        0 - unauthorized user
        1 - user in main menu
        2 - user in progress menu
        3 - user in studding menu (select topic)
        4 - user read theory
        5 - user pass test


    All methods returns next user step
    """

    def __init__(self, bot: TeleBot, message: types.Message, user: Student):
        """
        :param bot: TeleBot object for working with telegram API
        :param message: Message object from user
        :param user: Student object, need for getting student info
        :return StudentLogic object
        """
        self.bot = bot
        self.message = message
        self.user = user

    def check_token(self) -> int:
        """
        Check user token on valid and login user
        :return None
        """

        token = str(self.message.text)
        student_settings = StudentSettings.objects.filter(token=token).first()

        if not student_settings:
            self.bot.send_message(self.message.chat.id, msg['login_failed'])
            return 0

        if student_settings.student.step != 0:
            self.bot.send_message(self.message.chat.id, get_message_text('user_already_authorized', msg['user_already_authorized'], student_settings.student))
            return 0
        else:
            student_settings.student.user_id = self.message.chat.id
            student_settings.student.step = 1
            student_settings.student.save()
            self.bot.send_message(self.message.chat.id, get_message_text('login_succeeded', msg['login_succeeded'], student_settings.student))
            self.user = student_settings.student
            self.main_menu()
            return 1

    def welcome(self) -> int:
        """
        Checking auth and changed user step if he authorised
        :return: int (current student step)
        """
        if not self.user:
            self.bot.send_message(self.message.chat.id, get_message_text('input_token', msg['key_enter'], bot_token=self.bot.token))
            return 0
        return self.main_menu()

    def main_menu(self) -> int:
        """
        Send message with main_menu
        :return: 1
        """
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton('Учиться', callback_data='studding'),
                   types.InlineKeyboardButton('Мой Прогресс', callback_data='progress'))

        text_message = get_message_text('main_menu', msg['main_menu'], self.user)

        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=text_message,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(self.message.chat.id, text_message, reply_markup=markup)
        return 1

    def studding(self) -> int:
        """
        Send message with studding menu
        :return: 3
        """
        markup = types.InlineKeyboardMarkup(row_width=2)
        topics = TheoryTopic.objects.filter(restaurant=self.user.staff.restaurant_branch.main_restaurant).all()
        last_topic = None
        for topic in topics:
            student_topic = StudentTheoryTopic.objects.filter(student=self.user, theory_topic=topic).first()
            if student_topic.blocked and last_topic and last_topic.finished:
                student_topic.blocked = True
                student_topic.save()
            if student_topic.finished:
                emoj = '✅'
            elif not student_topic.blocked:
                emoj = '🔓'
            else:
                emoj = '🔒'
            last_topic = student_topic
            markup.add(types.InlineKeyboardButton(f'{emoj} {topic.name}', callback_data=f'topic_{topic.pk}_0'))

        markup.add(types.InlineKeyboardButton('Назад', callback_data='main_menu'))

        text_message = get_message_text('studding', msg['studding'], self.user)

        try:
            self.bot.edit_message_text(text=text_message, chat_id=self.message.chat.id,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(text=text_message, chat_id=self.message.chat.id,
                                  reply_markup=markup)
        return 3

    def progress(self) -> int:
        """
        Send message with user progress (opened/closed topics, tests results, opened questions)
        :return: 2
        """
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton('Назад', callback_data='main_menu'))

        topics = TheoryTopic.objects.filter(restaurant=self.user.staff.restaurant_branch).all()
        progress_text = ""
        for topic in topics:
            student_topic = StudentTheoryTopic.objects.filter(student=self.user, theory_topic=topic).first()
            topic_text = f"{topic.name} {'Открыт' if not student_topic.blocked else 'Закрыт'}\n"
            student_test = StudentTest.objects.filter(test=topic.test, student=self.user).first()
            if student_test:
                topic_text += f'''\t
{f"Пройден: {student_test.points}/{student_test.max_points} {f'Открытых вопросов {student_test.opened_questions}/{student_test.max_opened_questions}' if student_test.max_opened_questions else ''}" if student_test else "Не пройден"}\n\n'''
            progress_text += topic_text

        text_message = get_message_text('progress', msg['progress'], self.user).format(progress_text)

        try:
            self.bot.edit_message_text(text=text_message, chat_id=self.message.chat.id,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(text=text_message, chat_id=self.message.chat.id,
                                  reply_markup=markup)
        return 2

    def view_topic(self, topic_id: int, block_id: int) -> int:
        """

        :param topic_id: topic for get in bd
        :param block_id: number of block to view
        :return: 4
        """

        try:
            topic = TheoryTopic.objects.get(pk=topic_id)
        except TheoryTopic.DoesNotExist:
            self.bot.send_message(text=msg.get('topic_not_found'), chat_id=self.message.chat.id)
            return self.studding()

        student_topic = StudentTheoryTopic.objects.filter(student=self.user, theory_topic=topic).first()
        if not student_topic:
            self.bot.send_message(text=msg.get('topic_not_found'), chat_id=self.message.chat.id)
            return self.studding()

        if student_topic.blocked:
            self.bot.send_message(text=msg.get('test_before_next_lesson'), chat_id=self.message.chat.id)
            return self.studding()

        blocks = topic.blocks.all()
        markup = types.InlineKeyboardMarkup(row_width=3)
        tool_buttons = []

        if block_id != 0:
            tool_buttons.append(types.InlineKeyboardButton('Назад', callback_data=f'topic_{topic_id}_{block_id - 1}').to_dict())

        tool_buttons.append(types.InlineKeyboardButton('К разделу', callback_data='studding').to_dict())

        if block_id < len(blocks) - 1:
            tool_buttons.append(types.InlineKeyboardButton('Дальше', callback_data=f'topic_{topic_id}_{block_id + 1}').to_dict())
        else:
            student_topic.complete_theory = True
            student_topic.save()
            if topic.test:
                tool_buttons.append(types.InlineKeyboardButton('Пройти тест', callback_data=f'test_{topic.test.pk}_-1').to_dict())
            else:
                tool_buttons.append(types.InlineKeyboardButton('Завершить раздел', callback_data=f'completetopic_{topic_id}').to_dict())

        text_message = get_message_text('topic', msg['topic'], self.user).format(blocks[block_id].name,
                                                                                 blocks[block_id].text)

        markup.keyboard.append(tool_buttons)
        self.bot.edit_message_text(text=text_message, chat_id=self.message.chat.id,
                                   reply_markup=markup, message_id=self.message.message_id)
        return 4

    def view_test(self, test_id: int, question_id: int) -> int:
        """
        view test or test questions
        :param test_id: test for get in bd
        :param question_id: number of question
        :return: 5
        """
        try:
            test = TheoryTest.objects.get(pk=test_id)
            student_test = StudentTest.objects.filter(test=test, student=self.user, is_finished=False).first()
            if not student_test:
                student_test = StudentTest(test=test, student=self.user)
                student_test.save()
        except TheoryTest.DoesNotExist:
            self.bot.send_message(text=msg.get('test_not_found'), chat_id=self.message.chat.id)
            return self.studding()

        if question_id == test.questions.count():
            return self.pass_test(test, student_test)

        markup = types.InlineKeyboardMarkup(row_width=2)
        # start test
        if question_id == -1:
            markup.add(types.InlineKeyboardButton('Назад к теории', callback_data=f'topic_{test.theorytopic.pk}_{test.theorytopic.blocks.count() - 1}'),
                       types.InlineKeyboardButton('Начать тест', callback_data=f'test_{test_id}_0'))
            text_message = f'{test.name}'
            try:
                self.bot.edit_message_text(text=text_message, chat_id=self.message.chat.id,
                                           message_id=self.message.message_id, reply_markup=markup)
            except apihelper.ApiException:
                self.bot.send_message(text=text_message, chat_id=self.message.chat.id,
                                      reply_markup=markup)

            return 5
        else:
            all_questions = test.questions.all()
            if not all_questions[question_id].is_opened:
                # fill variants
                student_answers_tmp = student_test.answers.all()
                student_answers = []
                for temp_answ in student_answers_tmp:
                    if temp_answ.answer:
                        student_answers.append(temp_answ.answer.pk)
                for answer in all_questions[question_id].answers.all():
                    # stick or square
                    markup.add(types.InlineKeyboardButton(f'{"✔" if answer.pk in student_answers else "🔳"} {answer.answer}',
                                                          callback_data=f'answer_{student_test.pk}_{question_id}_{answer.pk}'))

        # last question
        if question_id == test.questions.count() - 1:
            markup.add(types.InlineKeyboardButton('⬅', callback_data=f'test_{test_id}_{question_id - 1}'),
                       types.InlineKeyboardButton('Завершить тест', callback_data=f'test_{test_id}_{question_id+1}'))
        # first question
        elif question_id == 0:
            markup.add(types.InlineKeyboardButton('➡', callback_data=f'test_{test_id}_{question_id + 1}'))
            self.user.current_test = student_test.pk
            self.user.current_open_question = None
            self.user.save()
        # another questions
        else:
            markup.add(types.InlineKeyboardButton('⬅', callback_data=f'test_{test_id}_{question_id - 1}'),
                       types.InlineKeyboardButton('➡', callback_data=f'test_{test_id}_{question_id + 1}'))

        if not all_questions[question_id].is_opened:
            text_message = f"Вопрос {question_id + 1}.\n\n{all_questions[question_id].question}"
        else:
            text_message = f"Вопрос {question_id + 1}.\n\n{all_questions[question_id].question}\n\n" \
                           f"Это открытый вопрос, напишите на него ответ, он будет отправлен на проверку\n"
            answer = student_test.answers.filter(question=all_questions[question_id]).first()
            if answer:
                text_message += f"Ваш текущий ответ: {answer.text if answer.text else 'Не отправлен'}"
            else:
                text_message += "Ваш текущий ответ: Не отправлен"
            if not answer:
                answer = StudentAnswer(student=self.user, question=all_questions[question_id])
                answer.save()
                student_test.answers.add(answer)
                self.user.current_open_question = answer.pk
                self.user.save()

        try:
            self.bot.edit_message_text(text=text_message, chat_id=self.message.chat.id,
                                       message_id=self.message.message_id, reply_markup=markup)
        except apihelper.ApiException:
            self.bot.send_message(text=text_message, chat_id=self.message.chat.id,
                                  reply_markup=markup)

        return 5

    def select_answer(self, student_test_id: int, question_id: int, answer_id: int) -> int:
        """

        :param student_test_id: student test id for bd
        :param question_id: number of question
        :param answer_id: number of answer
        :return: view_test()
        """
        student_test = StudentTest.objects.filter(pk=student_test_id).first()
        if not student_test:
            self.bot.send_message(text=msg.get('test_not_found'), chat_id=self.message.chat.id)
            return self.studding()
        try:
            question = student_test.test.questions.all()[question_id]
            answer = TestAnswer.objects.get(pk=answer_id)
        except IndexError:
            self.bot.send_message(text=msg.get('test_not_found'), chat_id=self.message.chat.id)
            return self.view_test(student_test.test.pk, question_id)
        except TestAnswer.DoesNotExist:
            self.bot.send_message(text=msg.get('answer_not_found'), chat_id=self.message.chat.id)
            return self.view_test(student_test.test.pk, question_id)

        student_answer = StudentAnswer(student=self.user, question=question, answer=answer)
        student_answer.save()
        for answ in student_test.answers.all():
            if answ.question == question:
                answ.delete()
        student_test.answers.add(student_answer)
        student_test.save()
        return self.view_test(student_test.test.pk, question_id)

    def add_open_answer(self) -> int:
        """
        write student answer to db and redirect to next question
        :return: view_test()
        """
        answer_text = self.message.text
        student_test = StudentTest.objects.filter(pk=self.user.current_test).first()

        try:
            test = TheoryTest.objects.get(pk=self.user.current_test)
        except TheoryTest.DoesNotExist:
            self.bot.send_message(text=msg.get('test_not_found'), chat_id=self.message.chat.id)
            return self.progress()

        try:
            student_answer = StudentAnswer.objects.get(pk=self.user.current_open_question)
        except StudentAnswer.DoesNotExist:
            self.bot.send_message(text=msg.get('answer_not_found'), chat_id=self.message.chat.id)
            return self.view_test(test.pk, 0)

        student_answer.text = answer_text
        student_answer.save()
        self.bot.send_message(text=msg.get('answer_writen'), chat_id=self.message.chat.id)
        question_id = self.user.current_open_question
        self.user.current_open_question = None
        self.user.save()
        i = 0
        for question in student_test.test.questions.all():
            if question.pk == question_id:
                break
            i += 1

        return self.view_test(test.pk, i)

    def pass_test(self, test: TheoryTest, student_test: StudentTest) -> int:
        """
        check test answers, write to db and close test
        :param test:
        :param student_test:
        :return: progress()
        """
        student_test.max_points = 0
        student_test.points = 0
        student_test.max_opened_questions = 0
        student_test.opened_questions = 0

        for question in test.questions.all():
            if question.is_opened:
                student_test.max_opened_questions += 1
                continue
            else:
                student_test.max_points += 1
            is_right = False
            for student_answer in student_test.answers.filter(question__is_opened=False).all():
                if is_right:
                    break
                for answer in question.answers.all():
                    if student_answer.answer.pk == answer.pk and answer.is_right:
                        student_test.points += 1
                        is_right = True
                        break
        student_test.is_finished = True
        student_theory_topic = StudentTheoryTopic.objects.filter(student=self.user, theory_topic=test.theorytopic).first()
        if student_theory_topic:
            if student_test.points / student_test.max_points > 0.5:
                student_theory_topic.complete_test = True
            else:
                student_theory_topic.complete_test = False
            student_theory_topic.finished = True
            student_theory_topic.save()

        student_test.save()
        self.user.current_test = None
        self.user.save()
        return self.progress()

    def message_in_test(self) -> int:
        """
        Send alert when user do something wrong on time test
        :return: 5
        """
        self.bot.send_message(self.message.chat.id, "Это действие запрещено во время теста")
        return 5














