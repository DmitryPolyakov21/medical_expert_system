# test_integration_diagnosis.py
import pytest
import requests
from django.test import Client
from expert_system.models import Symptom, Disease, MedicalRule

@pytest.mark.django_db
def test_cross_service_communication(settings):
    
    # 1. Подготовка данных
    symptom = Symptom.objects.create(name="cough", description="...")
    disease = Disease.objects.create(name="flu", description="...")
    
    MedicalRule.objects.create(
        name="Test Rule",
        conditions={"all": [{"fact": "symptom", "operator": "equal", "value": "cough"}]},
        action={"then": [{"fact": "disease", "set": "flu", "probability": 90.0}]}
    )

    # 2. Используем правильные URL из urls.py
    client = Client()
    
    # Главная страница (diagnose)
    response = client.post(
        "/",  # Основной URL, как указано в urls.py
        {"symptoms": [symptom.id]},
        HTTP_X_FORWARDED_FOR="185.143.172.42"
    )
    
    assert response.status_code == 200
    
    # Проверка статистики
    stats_response = client.get("/region-stats/?region=Москва")
    assert stats_response.status_code == 200
    
    # 5. Проверяем, что данные дошли до Analytics
    stats_response = requests.get(
        f"{settings.ANALYTICS_SERVICE_URL}/api/v1/stats/region/Москва",
        timeout=3
    )
    
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    
