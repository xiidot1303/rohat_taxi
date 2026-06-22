from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from app.models import *

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ("title", "is_intercity", "is_active", "city_id")
    search_fields = ("title", "city_id")

@admin.register(Street)
class StreetAdmin(ModelAdmin):
    list_display = ("title", "city")
    search_fields = ("title",)
    list_filter = ("city",)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "status",
        "src_street",
        "dst_street",
        "service_id",
        "start_time",
        "end_time",
    )
    list_filter = (
        "status",
        "service_id",
        "user",
        "start_time",
    )
    search_fields = (
        "order_id",
        "uuid",
        "src_street",
        "dst_street",
        "src_house",
        "dst_house",
        "user__name",
        "user__phone",
        "user__username",
    )
    ordering = ("-start_time",)


class ChequeAutonumFilter(admin.SimpleListFilter):
    title = "Госномер авто"
    parameter_name = "cheque_autonum"

    def lookups(self, request, model_admin):
        autonums = (
            Cheque.objects.exclude(autonum__isnull=True)
            .exclude(autonum="")
            .order_by("autonum")
            .values_list("autonum", flat=True)
            .distinct()
        )
        return [(autonum, autonum) for autonum in autonums]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cheque__autonum=self.value())

        return queryset


class ChequeDetailsMixin:
    @admin.display(description="ID чека", ordering="cheque__id")
    def cheque_id(self, obj):
        return obj.cheque_id

    @admin.display(description="Авто", ordering="cheque__autonum")
    def cheque_car_details(self, obj):
        if not obj.cheque:
            return "-"

        car_details = [
            obj.cheque.brand,
            obj.cheque.model,
            obj.cheque.color,
            obj.cheque.autonum,
        ]
        return " ".join(part for part in car_details if part) or "-"


class OrderReviewInline(TabularInline):
    model = OrderReview
    extra = 0
    fields = ("comment",)
    readonly_fields = ("comment",)
    tab = True

class OrderRatingInline(TabularInline):
    model = OrderRating
    extra = 0
    fields = ("rating", "reason")
    readonly_fields = ("rating", "reason")
    tab = True


@admin.register(OrderReview)
class OrderReviewAdmin(ChequeDetailsMixin, ModelAdmin):
    list_display = (
        "id",
        "cheque_id",
        "cheque_car_details",
        "user",
        "comment",
    )
    list_filter = (ChequeAutonumFilter, "user")
    search_fields = (
        "cheque__id",
        "cheque__autonum",
        "cheque__brand",
        "cheque__model",
        "cheque__color",
        "user__name",
        "user__phone",
        "user__username",
        "comment",
    )
    autocomplete_fields = ("cheque", "user")


@admin.register(OrderRating)
class OrderRatingAdmin(ChequeDetailsMixin, ModelAdmin):
    list_display = (
        "id",
        "cheque_id",
        "cheque_car_details",
        "user",
        "reason",
        "rating",
    )
    list_filter = (ChequeAutonumFilter, "rating", "reason", "user")
    search_fields = (
        "cheque__id",
        "cheque__autonum",
        "cheque__brand",
        "cheque__model",
        "cheque__color",
        "user__name",
        "user__phone",
        "user__username",
        "reason__text_ru",
        "reason__text_uz",
    )
    autocomplete_fields = ("cheque", "user", "reason")


@admin.register(Cheque)
class ChequeAdmin(ModelAdmin):
    list_display = (
        "id",
        "phonenum",
        "name",
        "status_code",
        "street",
        "house",
        "amount",
        "datetime",
    )
    list_filter = (
        "status_code",
        "brand",
        "model",
        "datetime",
    )
    search_fields = (
        "phonenum",
        "name",
        "street",
        "house",
        "code",
        "car_phone",
        "car_firstname",
        "autonum",
        "uuid",
    )
    inlines = [OrderReviewInline, OrderRatingInline]
    ordering = ("-datetime",)


@admin.register(RatingReason)
class RatingReasonAdmin(ModelAdmin):
    list_display = ["text_uz", "text_ru"]
    search_fields = ("text_uz", "text_ru")
