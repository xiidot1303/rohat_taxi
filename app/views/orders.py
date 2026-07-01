from datetime import datetime

from django.shortcuts import render

from app.models import Cheque, Order
from bot.models import Bot_user


TEXTS = {
    'ru': {
        'page_title': 'История заказов',
        'title': 'История заказов',
        'subtitle': 'Список завершённых поездок для выбранного пользователя Telegram.',
        'date_from': 'С даты',
        'date_to': 'По дату',
        'show': 'Показать',
        'user_label': 'Пользователь',
        'no_orders': 'Заказов за выбранный период не найдено.',
        'no_cheque': 'Детали чека не найдены.',
        'route': 'Маршрут',
        'house': 'Дом',
        'cheque': 'Чек',
        'amount': 'Сумма',
        'order': 'Заказ',
    },
    'uz': {
        'page_title': 'Buyurtmalar tarixi',
        'title': 'Buyurtmalar tarixi',
        'subtitle': 'Tanlangan Telegram foydalanuvchi uchun tugallangan safarlar ro‘yxati.',
        'date_from': 'Dan',
        'date_to': 'Gacha',
        'show': 'Ko‘rsatish',
        'user_label': 'Foydalanuvchi',
        'no_orders': 'Tanlangan davrda buyurtma topilmadi.',
        'no_cheque': 'Chek tafsilotlari topilmadi.',
        'route': 'Marshrut',
        'house': 'Uy',
        'cheque': 'Chek',
        'amount': 'Summa',
        'order': 'Buyurtma',
    },
}


def order_history(request):
    bot_user_id_value = (request.GET.get('bot_user_id') or request.GET.get('user_id') or '').strip()
    lang = (request.GET.get('lang') or 'ru').strip().lower()
    if lang not in TEXTS:
        lang = 'ru'

    start_date = (request.GET.get('start_date') or '').strip()
    end_date = (request.GET.get('end_date') or '').strip()

    error_message = None
    bot_user = None
    orders = Order.objects.none()
    rows = []

    if bot_user_id_value:
        try:
            bot_user_id = int(bot_user_id_value)
        except ValueError:
            error_message = 'Invalid bot user id'
        else:
            bot_user = Bot_user.objects.filter(user_id=bot_user_id).first()
            orders = Order.objects.filter(user__user_id=bot_user_id, end_time__isnull=False).order_by('-end_time')

            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    error_message = 'Invalid start date'
                else:
                    orders = orders.filter(end_time__gte=start_dt)

            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                except ValueError:
                    error_message = 'Invalid end date'
                else:
                    orders = orders.filter(end_time__lte=end_dt.replace(hour=23, minute=59, second=59, microsecond=999999))

            if not error_message and start_date and end_date:
                try:
                    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
                        error_message = 'Start date cannot be later than end date'
                except ValueError:
                    pass

            if not error_message:
                cheque_ids = [order.order_id for order in orders if order.order_id and str(order.order_id).isdigit()]
                cheques = {cheque.id: cheque for cheque in Cheque.objects.filter(pk__in=cheque_ids)} if cheque_ids else {}
                for order in orders:
                    cheque = None
                    if order.order_id and str(order.order_id).isdigit():
                        cheque = cheques.get(int(order.order_id))
                    rows.append({'order': order, 'cheque': cheque})
    else:
        error_message = 'Please provide a bot_user_id query parameter'

    return render(request, 'app/order_history.html', {
        'bot_user': bot_user,
        'bot_user_id': bot_user_id_value,
        'lang': lang,
        'texts': TEXTS[lang],
        'start_date': start_date,
        'end_date': end_date,
        'error_message': error_message,
        'orders': rows,
    })
