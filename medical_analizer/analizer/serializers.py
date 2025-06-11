from rest_framework import serializers
from .models import DiagnosisRecord

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisRecord
        fields = '__all__'
        extra_kwargs = {
            'symptoms': {'required': True},
            'diseases': {'required': True},
            'patient_ip': {'required': True}
        }
