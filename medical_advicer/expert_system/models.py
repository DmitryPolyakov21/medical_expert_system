from django.db import models

class Symptom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class MedicalRule(models.Model):
    name = models.CharField(max_length=100)
    conditions = models.JSONField()
    action = models.JSONField()
    priority = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
