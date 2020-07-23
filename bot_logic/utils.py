from .models import TelegramMessage


def get_message_text(tag, message, user) -> str:
    message_to_send = TelegramMessage.objects.filter(tag=tag, bot=user.telegram_bot).first()
    if not message_to_send:
        return message
    else:
        return message_to_send.text
