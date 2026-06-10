from bot.services import get_user_by_phone
from bot.services import string_service
from bot import Strings
from app.services.order_service import get_order_by_uuid_without_404, get_order_by_order_id_without_404
import json
from app.services.bot_service import send_newsletter_api

def send_cheque(phone, order_id):
    if user := get_user_by_phone(phone):
        order_obj = get_order_by_order_id_without_404(order_id)
        order = None
        src = ''
        dst = ''
        starttime = ''
        endtime = ''
        executor_id = ''
        amount = ''
        distance = ''
        standtime = ''
        waittime = ''
        street = src
        house = ''
        dststreet = ''
        dsthouse = ''
        try:
            taximeter_data = json.loads(order[13])
        except:
            taximeter_data = {}
        # get car info
        car_info = ['' for i in range(7)]
        autonum = car_info[0] or ''
        color = car_info[1] or ''
        brand = car_info[2] or ''
        model = car_info[3] or ''
        lastname = car_info[4] or ''
        firstname = car_info[5] or ''
        car_phone = car_info[6] or ''

        text = string_service.cheque_info(
            user.user_id, 
            src, dst, starttime, endtime, amount, distance,
            standtime, waittime, street, house, dststreet, dsthouse,
            autonum, color, brand, model, lastname, firstname, car_phone, taximeter_data
            )
        if order_obj:
            markup = [
                [{
                    "text": Strings(user_id = user.user_id).main_menu, 
                    "callback_data": 'main_menu'
                }]
            ]
        else:
            markup = None
        msg = send_newsletter_api(user.user_id, text, inline_buttons=markup)
        # if markup:
        #     # save context user_data
        #     dp.user_data[user.user_id]['last_msg'] = msg
        #     dp.user_data[user.user_id]['last_markup'] = markup
        return True
    else:
        return False

def send_order_status(phone, data):
    status_code = int(data['status_code'])
    if user := get_user_by_phone(phone):
        order = get_order_by_order_id_without_404(data['id'])
        markup = None
        keyboard_remove = False
        if status_code == 80:
            text = Strings(user_id=user.user_id).your_order_is_in_moderation
            
        elif status_code == 95:
            text = Strings(user_id=user.user_id).your_order_is_cancelled
            markup = [
                [{
                    "text": Strings(user_id = user.user_id).main_menu, 
                    "callback_data": 'main_menu'
                }]
            ]
        elif status_code == 10:
            text = string_service.car_info_string(
                user.user_id, data['remaining'], data['car_phone'], 
                data['car_firstname'],  data['brand'], data['model'], 
                data['color'], data['autonum']
            )
        elif status_code == 11:
            text = Strings(user_id=user.user_id).driver_is_here
        elif status_code == 4:
            text = Strings(user_id=user.user_id).order_is_in_execution
            keyboard_remove = True

        if not order:
            markup = None
        send_newsletter_api(user.user_id, text, inline_buttons=markup, keyboard_remove=keyboard_remove)
        return True
    else:
        return False 