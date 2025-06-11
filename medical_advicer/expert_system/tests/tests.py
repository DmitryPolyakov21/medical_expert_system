from django.test import TestCase, Client
from django.urls import reverse
from expert_system.models import Symptom, Disease, MedicalRule
from expert_system.views import diagnose, region_stats_view
from experta import KnowledgeEngine, Fact
from unittest.mock import patch, Mock
import requests


class ModelTests(TestCase):
    def test_models_creation(self):
        """
        Тестируем создание экземпляров моделей.
        """
        symptom = Symptom.objects.create(name="Headache", description="Pain in the head.")
        disease = Disease.objects.create(name="Flu", description="Common cold symptoms.")
        medical_rule = MedicalRule.objects.create(
            name="Test Rule",
            conditions={"headache": {"present": True}},
            action={"disease": "Flu", "value": 70},
            priority=1
        )

        self.assertEqual(str(symptom), "Headache")
        self.assertEqual(str(disease), "Flu")
        self.assertEqual(medical_rule.priority, 1)


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.diagnose_url = reverse("diagnosis")
        cls.region_stats_url = reverse("region_stats")

        # Создание тестовых данных
        Symptom.objects.create(name="Cough", description="Dry cough.")
        Symptom.objects.create(name="Fever", description="High body temperature.")
        Disease.objects.create(name="Flu", description="Common cold symptoms.")
        Disease.objects.create(name="COVID-19", description="Viral infection with respiratory symptoms.")

    def test_diagnose_get_request(self):
        """
        Тест GET-запроса на страницу диагностики.
        """
        response = self.client.get(self.diagnose_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "diagnose.html")
        self.assertIn(b"Cough", response.content)
        self.assertIn(b"Fever", response.content)

    def test_diagnose_post_request(self):
        """
        Тест POST-запроса на страницу диагностики.
        """
        data = {'symptoms': ['1']}  # Симптомы передаются в виде списка id
        response = self.client.post(self.diagnose_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "results.html")

    def test_region_stats_view(self):
        """
        Тест страницы статистики регионов.
        """
        response = self.client.get(self.region_stats_url + "?region=Москва")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "region_stats.html")


class ExpertSystemTests(TestCase):
    def test_medical_engine(self):
        """
        Тест работы экспертной системы (MedicalEngine).
        """
        from expert_system.engines import MedicalEngine, SymptomFact, DiseaseFact

        # Создание симулятора фактологии
        engine = MedicalEngine()
        engine.reset()

        # Добавляем факты о симптомах и заболеваниях
        headache_fact = SymptomFact(symptom='головная боль', present=True)
        flu_disease = DiseaseFact(name='грипп', probability=0.0)
        covid_disease = DiseaseFact(name='COVID-19', probability=0.0)

        engine.declare(headache_fact)
        engine.declare(flu_disease)
        engine.declare(covid_disease)

        # Запускаем систему вывода
        engine.run()

        # Проверяем изменение вероятностей
        diseases = [
            fact for fact in engine.facts.values() if isinstance(fact, DiseaseFact)
        ]
        self.assertGreater(len(diseases), 0)
        for disease in diseases:
            self.assertIsNotNone(disease["probability"])

    @patch.object(requests, 'post')
    def test_analytics_service_call(self, mock_post):
        """
        Тест отправки данных в аналитический сервис.
        """
        mock_response = Mock(status_code=200)
        mock_post.return_value = mock_response

        # Используем тестовую точку входа
        client = Client()
        data = {'symptoms': ['1']}
        response = client.post(reverse("diagnosis"), data=data)

        # Убедимся, что запрос отправлен
        mock_post.assert_called_once()
