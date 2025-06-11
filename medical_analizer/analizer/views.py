from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DiagnosisRecord
from .serializers import DiagnosisSerializer

@api_view(['POST'])
def receive_diagnosis(request):
    serializer = DiagnosisSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def region_stats(request, region_name):
    """Получение статистики по региону"""
    try:
        # Получаем параметры запроса
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))
        
        # Рассчитываем период
        from_date = timezone.now() - timedelta(days=days)
        
        # Формируем запрос
        stats = (
            DiagnosisRecord.objects
            .filter(
                Q(city__iexact=region_name) | Q(country__iexact=region_name),
                created_at__gte=from_date
            )
            .values('diseases')  # Группируем по заболеваниям
            .annotate(total=Count('id'))
            .order_by('-total')[:limit]  # Сортируем по убыванию и ограничиваем
        )
        
        # Форматируем результат
        diseases_stats = []
        for item in stats:
            try:
                disease_name = item['diseases'][0]['name']
                diseases_stats.append({
                    'disease': disease_name,
                    'cases': item['total']
                })
            except (IndexError, KeyError):
                continue
        
        return Response({
            'region': region_name,
            'period_days': days,
            'diseases': diseases_stats
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)
