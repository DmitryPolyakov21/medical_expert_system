from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .geoip import get_region_from_ip
import json

class DiagnosisRecord(models.Model):
    symptoms = models.JSONField()
    diseases = models.JSONField()
    patient_ip = models.CharField(max_length=15)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(pre_save, sender=DiagnosisRecord)
def add_geo_data(sender, instance, **kwargs):
    if instance.patient_ip and not instance.city:
        geo_data = get_region_from_ip(instance.patient_ip)
        instance.country = geo_data.get('country', '')
        instance.city = geo_data.get('city', '')
