from django.db.models import fields
from rest_framework import serializers
from app.models import *

class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheque
        # fields = '__all__'
        exclude = ['datetime']
