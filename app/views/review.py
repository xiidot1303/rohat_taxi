from django.http import Http404, JsonResponse
from django.shortcuts import render

from app.models import Cheque, OrderReview


TEXTS = {
    'ru': {
        'title': 'Оставьте отзыв',
        'subtitle': 'Поделитесь впечатлением о поездке и помогите нам стать лучше.',
        'label': 'Ваш комментарий',
        'button': 'Отправить отзыв',
        'thanks': 'Спасибо! Ваш отзыв сохранён.',
        'rating_label': 'Выберите оценку',
        'placeholder': 'Напишите, что понравилось или что можно улучшить...',
    },
    'uz': {
        'title': 'Fikr qoldiring',
        'subtitle': 'Safar haqidagi taassurobingizni yozing va bizni yaxshilashga yordam bering.',
        'label': 'Fikringiz',
        'button': 'Fikrni yuborish',
        'thanks': 'Rahmat! Fikringiz saqlandi.',
        'rating_label': 'Baholang',
        'placeholder': 'Safardagi taassurobingizni yozing — nimani yoqtirgansiz yoki yaxshilash kerak bo‘lsa, ayting.',
    },
}


def feedback_page(request, order_id, lang='ru'):
    try:
        cheque = Cheque.objects.get(pk=int(order_id))
    except (ValueError, Cheque.DoesNotExist):
        raise Http404('Cheque not found')

    texts = TEXTS.get(lang, TEXTS['ru'])

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0) or 0)
        comment = (request.POST.get('comment', '') or '').strip()

        if 1 <= rating <= 5:
            OrderReview.objects.create(cheque=cheque, rating=rating, comment=comment)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'message': texts['thanks']})

        return render(request, 'app/feedback.html', {
            'cheque': cheque,
            'lang': lang,
            'texts': texts,
            'submitted': True,
        })

    return render(request, 'app/feedback.html', {
        'cheque': cheque,
        'lang': lang,
        'texts': texts,
        'submitted': False,
    })
