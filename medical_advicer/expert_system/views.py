from django.shortcuts import render
from .engines import MedicalEngine, SymptomFact, DiseaseFact
from .models import Symptom, Disease
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
from .cities import capital_translation

logger = logging.getLogger(__name__)

@csrf_exempt
def diagnose(request):
    engine = MedicalEngine()
    engine.reset()
    
    if request.method == 'POST':
        symptom_ids = request.POST.getlist('symptoms')
        selected_symptoms = Symptom.objects.filter(id__in=symptom_ids)
        
        # Диагностика (ваш существующий код)
        for symptom in selected_symptoms:
            sf = SymptomFact(symptom=symptom.name.lower(), present=True)
            engine.declare(sf)
        
        for disease in Disease.objects.all():
            df = DiseaseFact(name=disease.name, probability=0.0)
            engine.declare(df)
        
        engine.run()
        
        # Собираем результаты
        diagnoses = []
        for fact in engine.facts.values():
            if isinstance(fact, DiseaseFact) and fact['probability'] > 0:
                diagnoses.append({
                    'name': fact['name'],
                    'probability': round(min(100, fact['probability']), 1),
                    'matched': fact['matched_symptoms'],
                    'total': fact['total_symptoms'],
                    'coverage': int((fact['matched_symptoms'] / fact['total_symptoms']) * 100)
                })

        # Подготовка данных для аналитики
        analytics_data = {
            'symptoms': [s.name for s in selected_symptoms],
            'diseases': [{
                'name': d['name'], 
                'probability': d['probability']
            } for d in diagnoses],
            'patient_ip': request.META.get('REMOTE_ADDR', '')
        }

        # Отправка в сервис аналитики
        try:
            response = requests.post(
                f"{settings.ANALYTICS_SERVICE_URL}/api/v1/diagnosis",
                json=analytics_data,
                timeout=3
            )
            if not response.ok:
                logger.error(f"Analytics service error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to send to analytics: {str(e)}")

        return render(request, 'results.html', {
            'diagnoses': sorted(diagnoses, key=lambda x: (-x['probability'], -x['coverage'])),
            'selected_symptoms': [s.name for s in selected_symptoms]
        })
    
    # GET запрос
    return render(request, 'diagnose.html', {
        'symptoms': Symptom.objects.all()
    })

def region_stats_view(request):
    # Получаем название региона из GET-параметра
    region_input = request.GET.get('region', 'Москва')  # По умолчанию Москва
    
    # Ищем город в базе
    city = capital_translation.get(region_input)
    
    # Если город найден, используем его английское название, иначе - оригинальный ввод
    region_for_api = city if city else region_input
    print(city)
    try:
        # Делаем GET-запрос к API аналитики
        response = requests.get(
            f"{settings.ANALYTICS_SERVICE_URL}/api/v1/stats/region/{region_for_api}",
            #params={'days': 30, 'limit': 10},
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('diseases', [])
            error = None
        else:
            stats = []
            error = f"Ошибка сервера: {response.status_code}"
            
    except Exception as e:
        stats = []
        error = f"Не удалось загрузить данные: {str(e)}"

    return render(request, 'region_stats.html', {
        'region': region_input,  # Возвращаем оригинальное название для отображения
        'stats': stats,
        'error': error
    })
