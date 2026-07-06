from django.db.models import fields
from rest_framework import serializers
from app.models import *

class ChequeSerializer(serializers.ModelSerializer):
    status_code = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Cheque
        # fields = '__all__'
        exclude = ['datetime']

    def get_validators(self):
        return []

    def validate_id(self, value):
        return value

    def validate(self, data):
        return data

    def save(self, **kwargs):
        cheque_id = self.validated_data.get('id')

        if cheque_id is not None:
            instance = Cheque.objects.filter(pk=cheque_id).first()
            if instance is not None:
                for field, value in self.validated_data.items():
                    if field == 'id':
                        continue
                    if value not in [None, '', [], {}]:
                        setattr(instance, field, value)

                instance.save()
                return instance

        create_data = self.validated_data.copy()
        return Cheque.objects.create(**create_data)