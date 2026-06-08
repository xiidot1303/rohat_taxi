from app.models import Order
# from app.services.postgresql_service import *
from app.services.scat_service import *

def filter_years_of_client_orders(bot_user):
    client_phone = bot_user.phone
    phone_id = get_phone_id(client_phone)
    if not phone_id:
        return None
    years = get_years_of_order(phone_id)
    return sorted(list(set(years)))

def filter_months_of_client_orders(bot_user, year):
    client_phone = bot_user.phone
    phone_id = get_phone_id(client_phone)
    months = get_months_of_order(phone_id, year)
    return sorted(list(set(months)))

def filter_days_of_client_orders(bot_user, year, month):
    client_phone = bot_user.phone
    phone_id = get_phone_id(client_phone)
    days = get_days_of_order(phone_id, year, month)
    return sorted(list(set(days)))

def filter_orders_by_date(bot_user, day, month, year):
    client_phone = bot_user.phone
    phone_id = get_phone_id(client_phone)
    orders = get_orders_by_date(phone_id, year, month, day)
    return orders


def create_order(
        bot_user, uuid, src, dst, 
        src_street=None, src_house=None, dst_street=None, dst_house=None, 
        src_lat=None, src_lon=None, dst_lon=None, dst_lat=None, service_id=None
    ):
    # check src status
    if src == 'location':
        # create order
        order = Order.objects.create(
            user = bot_user, uuid = uuid, src_street = src_street, src_house = src_house,
            src_lat = src_lat, src_lon = src_lon, service_id = service_id
        )
    elif src == 'address':
        # create order
        order = Order.objects.create(
            user = bot_user, uuid = uuid, src_street = src_street, 
            src_house = src_house, service_id = service_id
        )

    # check dst status
    if dst == 'location':
        order.dst_street = dst_street
        order.dst_house = dst_house
        order.dst_lon = dst_lon
        order.dst_lat = dst_lat
    elif src == 'address':
        order.dst_street = dst_street
        order.dst_house = dst_house
    # save changes
    order.save()

    return order

def get_order_by_id(id):
    obj = Order.objects.get(pk=id)
    return obj

def get_order_by_uuid_without_404(uuid):
    if orders := Order.objects.filter(uuid=uuid):
        order = orders[0]
        return order
    return None

def get_order_by_order_id_without_404(order_id):
    if orders := Order.objects.filter(order_id=str(order_id)):
        order = orders[0]
        return order
    return None

def change_order_status_by_uuid(uuid, order_id, status):
    if order := get_order_by_uuid_without_404(uuid):
        order.status = int(status)
        order.order_id = order_id
        order.save()
        return True
    return False

def change_order_status_by_order_id(order_id, status):
    if order := get_order_by_order_id_without_404(order_id):
        order.status = int(status)
        order.save()
        return True
    return False