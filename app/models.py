from django.db import models
from asgiref.sync import sync_to_async

class Language(models.Model):
    user_ip = models.CharField(null=True, blank=False, max_length=32)
    LANG_CHOICES = [(0, 'uz'), (1, 'ru'), (2, 'en')]
    lang = models.IntegerField(null=True, blank=True, choices=LANG_CHOICES)

class Cheque(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="ID заказа")
    street = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Улица")
    house = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Дом")
    phonenum = models.CharField(max_length = 255, verbose_name="Телефон")
    name = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Имя")
    remaining = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Оставшееся время")
    status_code = models.CharField(max_length = 255, verbose_name="Код статуса")
    code = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Код")
    car_phone = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Телефон водителя")
    car_firstname = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Имя водителя")
    car_photo = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Фото автомобиля")
    brand = models.CharField(max_length = 255, null=True, blank=True, default='', verbose_name="Марка")
    model = models.CharField(max_length = 255, null=True, blank=True, default='', verbose_name="Модель")
    color = models.CharField(max_length = 255, null=True, blank=True, default='', verbose_name="Цвет")
    autonum = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Госномер")
    amount = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Сумма")
    uuid = models.CharField(max_length = 255, null=True, blank=True, verbose_name="UUID")
    bonus = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Бонус")
    discount = models.CharField(max_length = 255, null=True, blank=True, verbose_name="Скидка")
    datetime = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name="Дата и время")

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"

class Order(models.Model):
    order_id = models.CharField(null=True, blank=True, max_length=64, verbose_name="ID заказа")
    user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Пользователь")
    uuid = models.CharField(null=True, blank=True, max_length=255, verbose_name="UUID")
    status = models.IntegerField(null=True, blank=True, verbose_name="Статус")
    src_street = models.CharField(null=True, blank=True, max_length=255, verbose_name="Улица отправления")
    src_house = models.CharField(null=True, blank=True, max_length=255, default='', verbose_name="Дом отправления")
    dst_street = models.CharField(null=True, blank=True, max_length=255, verbose_name="Улица назначения")
    dst_house = models.CharField(null=True, blank=True, max_length=255, default='', verbose_name="Дом назначения")
    src_lat = models.CharField(null=True, blank=True, max_length=255, verbose_name="Широта отправления")
    src_lon = models.CharField(null=True, blank=True, max_length=255, verbose_name="Долгота отправления")
    dst_lon = models.CharField(null=True, blank=True, max_length=255, verbose_name="Долгота назначения")
    dst_lat = models.CharField(null=True, blank=True, max_length=255, verbose_name="Широта назначения")
    service_id = models.IntegerField(null=True, blank=True, verbose_name="ID услуги")
    start_time = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name="Время начала")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
    address = models.CharField(null=True, blank=True, max_length=255, verbose_name="Адрес")
    passengers_count = models.IntegerField(null=True, blank=True, verbose_name="Количество пассажиров")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class City(models.Model): # Service
    title = models.CharField(max_length = 255, null=True, blank=False, verbose_name='Название')
    service_id = models.IntegerField(null=True, blank=False, unique=True, verbose_name='ID служб в SCAT')
    city_id = models.IntegerField(null=True, blank=False, verbose_name='ID города в SCAT')
    is_intercity = models.BooleanField(default=False, verbose_name="Межгород")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class Street(models.Model):
    title = models.CharField(max_length = 255, null=True, blank=False, verbose_name='Название')
    title_normalized = models.CharField(max_length = 255, null=True, blank=False)
    city = models.ForeignKey('app.City', blank=False, on_delete=models.PROTECT, verbose_name='Город')

    @property
    @sync_to_async
    def get_city(self) -> City:
        return self.city

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = "Улица"
        verbose_name_plural = "Улицы"


class OrderReview(models.Model):
    user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.SET_NULL)
    cheque = models.ForeignKey(Cheque, related_name='reviews', on_delete=models.CASCADE, verbose_name="Чек")
    comment = models.TextField(verbose_name="Комментарий", blank=True)

    class Meta:
        verbose_name = "Отзыв о заказе"
        verbose_name_plural = "Отзывы о заказах"

    def __str__(self):
        return f"Review for Cheque {self.cheque.id}"

class RatingReason(models.Model):
    text_uz = models.CharField(max_length=32)
    text_ru = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Причина оценки"
        verbose_name_plural = "Причины оценки"

    def __str__(self) -> str:
        return self.text_ru

class OrderRating(models.Model):
    user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.SET_NULL)
    cheque = models.ForeignKey(Cheque, null=True, related_name="ratings", on_delete=models.SET_NULL, verbose_name="Чек")
    reason = models.ForeignKey(RatingReason, null=True, on_delete=models.PROTECT, verbose_name="Причина")
    rating = models.PositiveIntegerField(verbose_name="Оценка", choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        verbose_name = "Оценка заказа"
        verbose_name_plural = "Оценки заказа"


class Feedback(models.Model):
    bot_user = models.ForeignKey(
        'bot.Bot_user', null=True, blank=True, related_name='feedbacks',
        on_delete=models.SET_NULL, verbose_name='Пользователь'
        )
    message = models.TextField(null=True, blank=True, max_length=2500, verbose_name='Сообщение')
    datetime = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name='Дата')

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class FavoriteAddress(models.Model):
    bot_user = models.ForeignKey(
        'bot.Bot_user', null=True, blank=True, related_name='favorite_addresses',
        on_delete=models.SET_NULL, verbose_name='Пользователь'
        )
    address = models.CharField(null=True, blank=True, max_length=255, verbose_name='Адрес')
    lat = models.CharField(null=True, blank=True, max_length=255, verbose_name='Широта')
    lon = models.CharField(null=True, blank=True, max_length=255, verbose_name='Долгота')

    class Meta:
        verbose_name = "Избранный адрес"
        verbose_name_plural = "Избранные адреса"