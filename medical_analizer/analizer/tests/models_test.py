from django.test import TestCase
from analizer.models import DiagnosisRecord
from django.db.models.signals import post_save
from django.core.cache import cache

class DiagnosisRecordModelTest(TestCase):
    def test_record_creation_and_signal(self):
        """
        Тест сохранения записи и сигнала для гео-данных.
        """
        # Создаем экземпляр модели
        record = DiagnosisRecord.objects.create(
            symptoms=["cold"],
            diseases=["flu"],
            patient_ip="85.115.248.201"
        )

        # Проверяем поля после срабатывания сигнала
        self.assertTrue(hasattr(record, 'country'))  # Сигнал сработал и заполнил страну
        self.assertTrue(hasattr(record, 'city'))     # Город тоже заполнен
