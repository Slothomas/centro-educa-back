from rest_framework import serializers # type: ignore
from .models import Profesor

class ProfesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesor
        fields = '__all__'
