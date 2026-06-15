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
        # Remove unique validators on id field entirely
        return []

    def validate_id(self, value):
        # For updates (status_code != 1), id must exist in DB
        status_code = int(self.initial_data.get('status_code'))
        if status_code != 1:
            if not Cheque.objects.filter(pk=value).exists():
                raise serializers.ValidationError("Object with this id does not exist.")
        return value

    def validate(self, data):
        status_code = int(data.get('status_code'))
        if status_code != 1 and not data.get('id'):
            raise serializers.ValidationError({"id": "This field is required for updates."})
        return data

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        if not valid and self.errors.get('id') and 'This field is required for updates.' in self.errors['id']:
            # If the error is about 'id' being required, we can ignore it for creation
            self._errors.pop('id')
            return True
        return valid

    def save(self, **kwargs):
        status_code = int(self.validated_data.pop('status_code'))
        if status_code == 1:
            # CREATE
            return Cheque.objects.create(**self.validated_data)
        else:
            # UPDATE — only non-blank fields
            id = self.validated_data.pop('id')
            instance = Cheque.objects.get(id=id)

            for field, value in self.validated_data.items():
                if value not in [None, '', [], {}]:  # skip blank values
                    setattr(instance, field, value)

            instance.save()
            return instance