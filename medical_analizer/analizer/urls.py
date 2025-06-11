from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/diagnosis', views.receive_diagnosis, name='diagnosis-api'),
    path('api/v1/stats/region/<str:region_name>', views.region_stats),
]
