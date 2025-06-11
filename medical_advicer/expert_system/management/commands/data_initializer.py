from django.apps import apps
from django.core.management.base import BaseCommand

class DataInitializer:
    def __init__(self):
        self.Symptom = apps.get_model('expert_system', 'Symptom')
        self.Disease = apps.get_model('expert_system', 'Disease')
        self.MedicalRule = apps.get_model('expert_system', 'MedicalRule')

    def initialize(self):
        self._create_symptoms()
        self._create_diseases()
        self._create_rules()
        print("Инициализация данных завершена")

    def _create_symptoms(self):
        symptoms = [
            {'name': 'Головная боль', 'description': 'Боль в области головы'},
            {'name': 'Температура', 'description': 'Повышенная температура тела'},
            {'name': 'Кашель', 'description': 'Рефлекторное очищение дыхательных путей'},
            {'name': 'Сыпь', 'description': 'Кожные высыпания различного характера'},
            {'name': 'Слабость', 'description': 'Общее недомогание и усталость'}
        ]
        
        for symptom_data in symptoms:
            self.Symptom.objects.get_or_create(
                name=symptom_data['name'],
                defaults={'description': symptom_data['description']}
            )
        print(f"Создано {len(symptoms)} симптомов")

    def _create_diseases(self):
        diseases = [
            {'name': 'Грипп', 'description': 'Острое вирусное заболевание дыхательных путей'},
            {'name': 'Корь', 'description': 'Острое инфекционное вирусное заболевание'},
            {'name': 'ОРВИ', 'description': 'Острая респираторная вирусная инфекция'},
            {'name': 'Ангина', 'description': 'Воспаление небных миндалин'}
        ]
        
        for disease_data in diseases:
            self.Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults={'description': disease_data['description']}
            )
        print(f"Создано {len(diseases)} заболеваний")

    def _create_rules(self):
        # Получаем объекты симптомов и заболеваний
        headache = self.Symptom.objects.get(name='Головная боль')
        fever = self.Symptom.objects.get(name='Температура')
        cough = self.Symptom.objects.get(name='Кашель')
        rash = self.Symptom.objects.get(name='Сыпь')
        
        flu = self.Disease.objects.get(name='Грипп')
        measles = self.Disease.objects.get(name='Корь')

        rules = [
            {
                'name': 'Правило гриппа',
                'priority': 10,
                'conditions': [
                    {'symptom': headache.name, 'present': True},
                    {'symptom': fever.name, 'present': True},
                    {'symptom': cough.name, 'present': True}
                ],
                'action': {
                    'disease': flu.name,
                    'value': 85.0,
                    'min_threshold': 0.3  # 30% совпадений
                }
            },
            {
                'name': 'Правило кори',
                'priority': 9,
                'conditions': [
                    {'symptom': fever.name, 'present': True},
                    {'symptom': rash.name, 'present': True}
                ],
                'action': {
                    'disease': measles.name,
                    'value': 90.0,
                    'min_threshold': 0.5  # 50% совпадений
                }
            }
        ]

        for rule_data in rules:
            rule, created = self.MedicalRule.objects.get_or_create(
                name=rule_data['name'],
                defaults={
                    'priority': rule_data['priority'],
                    'conditions': rule_data['conditions'],
                    'action': rule_data['action']
                }
            )
            if created:
                print(f"Создано правило: {rule.name}")
            else:
                rule.conditions = rule_data['conditions']
                rule.action = rule_data['action']
                rule.save()
                print(f"Обновлено правило: {rule.name}")

class Command(BaseCommand):
    help = 'Инициализирует начальные данные в БД'

    def handle(self, *args, **options):
        initializer = DataInitializer()
        initializer.initialize()
        self.stdout.write(self.style.SUCCESS('Данные успешно инициализированы'))
