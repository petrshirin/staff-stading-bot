from django.http import HttpResponse
from .models import *
from telebot import TeleBot, types
import logging
import json
from .student_controllers import StudentLogic

# Create your views here.

LOG = logging.getLogger(__name__)
bot = TeleBot('')


def get_web_hook(request, token):
    bot_orm = TelegramBot.objects.filter(token=token).first()
    json_data = json.loads(request.body)
    if not bot_orm:
        LOG.error('fail bot')
        return HttpResponse('fail bot', status=500)
    LOG.debug(str(json_data).encode('utf-8'))
    global bot
    bot.token = bot_orm.token
    request_body_dict = json_data
    update = types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return HttpResponse('ok', status=200)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    telegram_bot = TelegramBot.objects.filter(token=bot.token).first()
    user = Student.objects.filter(telegram_bot=telegram_bot, user_id=message.chat.id).first()
    action = StudentLogic(bot, message, user)
    action.welcome()


@bot.message_handler(content_types=['text'])
def text_logic(message: types.Message):
    telegram_bot = TelegramBot.objects.filter(token=bot.token).first()
    user = Student.objects.filter(telegram_bot=telegram_bot, user_id=message.chat.id).first()
    action = StudentLogic(bot, message, user)
    if not user or user.step == 0:
        if not user:
            action.check_token()
        else:
            user.step = action.check_token()

    elif user.step == 5 and user.current_open_question:
        user.step = action.add_open_answer()

    elif user.step == 5:
        user.step = action.message_in_test()

    user.save()


@bot.callback_query_handler(func=lambda c: True)
def inline_logic(c):
    LOG.debug(c.data)
    user = Student.objects.get(user_id=c.message.chat.id)
    action = StudentLogic(bot, c.message, user)

    if c.data == "main_menu":
        user.step = action.main_menu()
    elif c.data == "studding":
        user.step = action.studding()
    elif c.data == "progress":
        user.step = action.progress()
    elif 'topic_' in c.data:
        try:
            param = c.data.split('_')
            topic_id = int(param[1])
            block_id = int(param[2])
        except Exception as err:
            LOG.error(err)
            return
        user.step = action.view_topic(topic_id, block_id)

    elif 'test_' in c.data:
        try:
            param = c.data.split('_')
            test_id = int(param[1])
            question_id = int(param[2])
        except Exception as err:
            LOG.error(err)
            return
        user.step = action.view_test(test_id, question_id)

    elif 'answer_' in c.data:
        try:
            param = c.data.split('_')
            student_test_id = int(param[1])
            question_id = int(param[2])
            answer_id = int(param[3])
        except Exception as err:
            LOG.error(err)
            return
        user.step = action.select_answer(student_test_id, question_id, answer_id)

    user.save()














