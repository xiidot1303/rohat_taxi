from django.db import models
from asgiref.sync import sync_to_async

class Language(models.Model):
    user_ip = models.CharField(null=True, blank=False, max_length=32)
    LANG_CHOICES = [(0, 'uz'), (1, 'ru'), (2, 'en')]
    lang = models.IntegerField(null=True, blank=True, choices=LANG_CHOICES)

class Cheque(models.Model):
    id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length = 255, null=True, blank=True)
    house = models.CharField(max_length = 255, null=True, blank=True)
    phonenum = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255, null=True, blank=True)
    remaining = models.CharField(max_length = 255, null=True, blank=True)
    status_code = models.CharField(max_length = 255)
    code = models.CharField(max_length = 255, null=True, blank=True)
    car_phone = models.CharField(max_length = 255, null=True, blank=True)
    car_firstname = models.CharField(max_length = 255, null=True, blank=True)
    car_photo = models.CharField(max_length = 255, null=True, blank=True)
    brand = models.CharField(max_length = 255, null=True, blank=True, default='')
    model = models.CharField(max_length = 255, null=True, blank=True, default='')
    color = models.CharField(max_length = 255, null=True, blank=True, default='')
    autonum = models.CharField(max_length = 255, null=True, blank=True)
    amount = models.CharField(max_length = 255, null=True, blank=True)
    uuid = models.CharField(max_length = 255, null=True, blank=True)
    bonus = models.CharField(max_length = 255, null=True, blank=True)
    discount = models.CharField(max_length = 255, null=True, blank=True)
    datetime = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True)

class Order(models.Model):
    order_id = models.CharField(null=True, blank=True, max_length=64)
    user = models.ForeignKey('bot.Bot_user', null=True, blank=True, on_delete=models.SET_NULL)
    uuid = models.CharField(null=True, blank=True, max_length=255)
    status = models.IntegerField(null=True, blank=True)
    src_street = models.CharField(null=True, blank=True, max_length=255)
    src_house = models.CharField(null=True, blank=True, max_length=255, default='')
    dst_street = models.CharField(null=True, blank=True, max_length=255)
    dst_house = models.CharField(null=True, blank=True, max_length=255, default='')
    src_lat = models.CharField(null=True, blank=True, max_length=255)
    src_lon = models.CharField(null=True, blank=True, max_length=255)
    dst_lon = models.CharField(null=True, blank=True, max_length=255)
    dst_lat = models.CharField(null=True, blank=True, max_length=255)
    service_id = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

class City(models.Model):
    title = models.CharField(max_length = 255, null=True, blank=False, verbose_name='Название')
    city_id = models.IntegerField(null=True, blank=False, unique=True, verbose_name='ID города в SCAT')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Города"
        verbose_name_plural = "Город"


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
    cheque = models.ForeignKey(Cheque, null=True, related_name="ratings", on_delete=models.SET_NULL, verbose_name="Чек")
    reason = models.ForeignKey(RatingReason, null=True, on_delete=models.PROTECT, verbose_name="Причина")
    rating = models.PositiveIntegerField(verbose_name="Оценка", choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        verbose_name = "Оценка заказа"
        verbose_name_plural = "Оценки заказа"
