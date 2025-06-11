from django.test import TestCase, RequestFactory
from analizer.views import receive_diagnosis, region_stats
from rest_framework.test import APIClient
from rest_framework import status
from analizer.models import DiagnosisRecord

class ApiViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_receive_diagnosis(self):
        """
        Тест приема нового диагноза.
        """
        response = self.client.post('/api/v1/diagnosis', {
            'symptoms': ["cold"],
            'diseases': ["flu"],
            'patient_ip': "85.115.248.201"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_region_stats(self):
        """
        Тест статистики по региону.
        """
        response = self.client.get('/api/v1/stats/region/Stavropol')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('diseases', response.data)
