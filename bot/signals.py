from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from bot.models import Bot_user, Message
from bot.services.redis_service import set_user_lang
from app.services.bot_service import send_newsletter_api
from django.conf import settings


@receiver(post_save, sender=Bot_user)
def save_bot_user_lang_to_redis(sender, instance: Bot_user, created, **kwargs):
    """
    Save the 'lang' of a bot user in Redis when a new user is created
    """
    if created:
        if instance.user_id is not None:
            set_user_lang(instance.user_id, instance.lang)


@receiver(pre_save, sender=Bot_user)
def handle_lang_change(sender, instance: Bot_user, **kwargs):
    """
    Handle changes to the 'lang' field specifically and update Redis.
    """
    if instance.pk:  # Check if the instance already exists
        try:
            original_instance = Bot_user.objects.get(pk=instance.pk)
            if original_instance.lang != instance.lang:
                set_user_lang(instance.user_id, instance.lang)
                
        except Bot_user.DoesNotExist:
            # If the instance does not exist in the database yet, do nothing
            pass


@receiver(post_save, sender=Message)
def send_message_to_users(sender, instance: Message, created, **kwargs):
    """
    Send a message to all users when a new message is created.
    """
    if created:
        users = instance.bot_users.all()
        if not users:
            users = Bot_user.objects.all()
        # photo=f"{settings.MEDIA_URL}/{instance.photo.name}" if instance.photo else None
        # video=f"{settings.MEDIA_URL}/{instance.video.name}" if instance.video else None
        # document=f"{settings.MEDIA_URL}/{instance.file.name}" if instance.file else None
        for user in users:
            send_newsletter_api.delay(
                bot_user_id=user.user_id,
                text=instance.text,
            )