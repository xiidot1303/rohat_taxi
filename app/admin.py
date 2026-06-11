from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
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
    list_display = ("title", "city_id")
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
    ordering = ("-datetime",)