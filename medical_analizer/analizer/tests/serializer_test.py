from django.test import TestCase
from analizer.serializers import DiagnosisSerializer
from analizer.models import DiagnosisRecord

class SerializerTest(TestCase):
    def test_serializer_validation(self):
        """
        Тест сериализатора.
        """
        serializer = DiagnosisSerializer(data={
            'symptoms': ["cold"],
            'diseases': ["flu"],
            'patient_ip': "85.115.248.201"
        })
        self.assertTrue(serializer.is_valid())

        invalid_data = serializer.data.copy()
        del invalid_data['symptoms']
        invalid_serializer = DiagnosisSerializer(data=invalid_data)
        self.assertFalse(invalid_serializer.is_valid())  # Без обязательных полей не проходит
