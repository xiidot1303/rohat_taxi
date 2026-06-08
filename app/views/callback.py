from django.http import HttpResponse, JsonResponse
from app.serializers import ChequeSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, generics
from app.services.order_service import *
from app.services import newsletter_service


@api_view(['GET', 'POST'])
def cheque_info(request):
    if request.method == 'GET':
        
        serializer = ChequeSerializer(data=request.GET)
        
        if serializer.is_valid():
            data = serializer.initial_data
            print(data)
            phone = data['phonenum']
            uuid = data['uuid']
            order_id = data['id']
            # check status and send message
            if data['status_code'] in ['80', '95', '10', '11', '4', '1']:
                if data['status_code'] == '1':
                    change_order_status_by_uuid(uuid, order_id, data['status_code'])
                else:
                    change_order_status_by_order_id(order_id, data['status_code'])
                    # send notification
                    newsletter_service.send_order_status(phone, data)

            elif data['status_code'] == '100':
                serializer.save()
                # send notification
                newsletter_service.send_cheque(
                    phone, data['id']
                )
                change_order_status_by_order_id(order_id, data['status_code'])
                return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    return JsonResponse({})


# <QueryDict: {'id': ['1008881'], 'street': [''], 'house': [''], 'phonenum': ['+998919800555'], 'name': [''], 'remaining': ['10'], 'status_code': ['100'], 'code': ['054'], 'car_phone': ['+998900065196'], 'car_firstname': ['Асадбек'], 'car_photo': [''], 'brand': ['Chevrolet'], 'model': ['Cobalt'], 'color': ['Белый'], 'autonum': ['054'], 'amount': ['10000.0000'], 'uuid': [''], 'bonus': [''], 'discount': ['']}>
# {'code': 80, 'name': 'На модерации'}} , operator qabul qilishi kk
# {'code': 95, 'name': 'Клиент отказался'}
# {'code': 10, 'name': 'Сообщили время подъезда'}  ///  'remaining': ['5']
# {'code': 11, 'name': 'Сообщили о подъезде машины'}} mashina yetib keldi
# 'code': 4, 'name': 'В исполнении'}}, start, yulda
# {'code': 100, 'name': 'Заказ выполнен'}}

# {'code': 9, 'name': 'Свободный'}}