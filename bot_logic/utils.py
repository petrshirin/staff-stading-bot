from .models import TelegramMessage, TelegramBot


def get_message_text(tag, message, user=None, bot_token: str = None) -> str:
    if bot_token:
        bot = TelegramBot.objects.filter(token=bot_token).first()
        if bot:
            message_to_send = TelegramMessage.objects.filter(tag=tag, bot=bot).first()
        else:
            message_to_send = None
    else:
        message_to_send = TelegramMessage.objects.filter(tag=tag, bot=user.telegram_bot).first()
    if not message_to_send:
        return message
    else:
        return message_to_send.text
