from django.contrib import admin
from .models import Symptom, Disease, MedicalRule

admin.site.register(Symptom)
admin.site.register(Disease)
admin.site.register(MedicalRule)
