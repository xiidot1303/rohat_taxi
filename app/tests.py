from datetime import datetime, timezone

from django.test import TestCase

from app.models import Cheque, Order, OrderReview
from bot.models import Bot_user


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.cheque = Cheque.objects.create(id=101, phonenum='+998901234567', status_code='done', amount='120000')

    def test_feedback_page_renders_for_cheque(self):
        response = self.client.get('/feedback/101/ru/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Оставьте отзыв')

    def test_feedback_submission_creates_review(self):
        response = self.client.post('/feedback/101/ru/', {
            'rating': 5,
            'comment': 'Отличная поездка',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrderReview.objects.filter(cheque=self.cheque, comment='Отличная поездка').exists())


class OrderHistoryViewTests(TestCase):
    def setUp(self):
        self.bot_user = Bot_user.objects.create(user_id=777, name='Test User')
        self.cheque = Cheque.objects.create(
            id=1001,
            phonenum='+998901234567',
            status_code='done',
            amount='120000',
            street='Main Street',
            house='10',
        )
        self.order_in_range = Order.objects.create(
            order_id='1001',
            user=self.bot_user,
            end_time=datetime(2024, 7, 15, 12, 0, tzinfo=timezone.utc),
        )
        self.order_out_of_range = Order.objects.create(
            order_id='1002',
            user=self.bot_user,
            end_time=datetime(2024, 6, 10, 12, 0, tzinfo=timezone.utc),
        )

    def test_order_history_filters_by_bot_user_and_date_range(self):
        response = self.client.get('/order-history?bot_user_id=777&start_date=2024-07-01&end_date=2024-07-31')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Main Street')
        self.assertNotContains(response, '1002')

    def test_order_history_supports_uzbek_language_and_hides_user_id(self):
        response = self.client.get('/order-history?bot_user_id=777&lang=uz&start_date=2024-07-01&end_date=2024-07-31')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buyurtmalar tarixi')
        self.assertNotContains(response, 'Bot user id')
