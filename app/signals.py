from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import OrderRating, OrderReview, Feedback
from app.services.newsletter_service import (
    send_order_rating_to_admin_group,
    send_order_review_to_admin_group,
    send_feedback_to_admin_group
)


@receiver(post_save, sender=OrderRating)
def order_rating_created(sender, instance: OrderRating, created, raw=False, **kwargs):
    if raw or not created:
        return

    transaction.on_commit(lambda: send_order_rating_to_admin_group(instance))


@receiver(post_save, sender=OrderReview)
def order_review_created(sender, instance: OrderReview, created, raw=False, **kwargs):
    if raw or not created:
        return

    transaction.on_commit(lambda: send_order_review_to_admin_group(instance))


@receiver(post_save, sender=Feedback)
def feedback_created(sender, instance: Feedback, created, raw=False, **kwargs):
    if raw or not created:
        return

    transaction.on_commit(lambda: send_feedback_to_admin_group(instance))