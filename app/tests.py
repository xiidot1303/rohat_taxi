from django.test import TestCase

from app.models import Cheque, OrderReview


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
        self.assertTrue(OrderReview.objects.filter(cheque=self.cheque, rating=5, comment='Отличная поездка').exists())
