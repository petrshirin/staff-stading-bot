from django.core.management.base import LabelCommand
import telebot
from django.apps import apps
from django.conf import settings

TelegramBot = apps.get_model('bot_telegram', 'TelegramBot')


class Command(LabelCommand):

    def handle(self, label, **options):
        try:
            telebot.TeleBot(label).delete_webhook()
            bot = TelegramBot.objects.get(token=label)
            telebot.TeleBot(label).set_webhook(f'{settings.WEBHOOK_HOST}/telegram_bot/{bot.token}')
            self.stdout.write('webhook installed')
        except Exception as err:
            self.stdout.write(err)
