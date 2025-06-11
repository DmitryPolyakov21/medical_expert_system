from experta import KnowledgeEngine, Rule, Fact, MATCH, TEST, NOT
from django.apps import apps

class SymptomFact(Fact):
    """Факт о симптоме"""
    pass

class DiseaseFact(Fact):
    """Факт о заболевании"""
    pass

class MedicalEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self._load_rules_once()
    
    def _load_rules_once(self):
        if hasattr(self.__class__, '_rules_loaded'):
            return
            
        MedicalRule = apps.get_model('expert_system', 'MedicalRule')
        Symptom = apps.get_model('expert_system', 'Symptom')
        
        self.valid_symptoms = {s.name.lower() for s in Symptom.objects.all()}
        
        for rule in MedicalRule.objects.all():
            try:
                self._create_rule(rule)
            except Exception as e:
                print(f"Ошибка в правиле {rule.id}: {str(e)}")
                continue
        
        self.__class__._rules_loaded = True
        print(f"Загружено правил: {MedicalRule.objects.count()}")

    def _create_rule(self, db_rule):
        """Создание правила с использованием MATCH и TEST"""
        if not hasattr(db_rule, 'action') or 'value' not in db_rule.action:
            print(f"Правило {db_rule.id} пропущено: некорректное действие")
            return

        # Получаем список симптомов правила в нижнем регистре
        rule_symptoms = {cond['symptom'].lower() for cond in db_rule.conditions}
        
        # Параметры правила
        disease_name = db_rule.action['disease']
        total_symptoms = len(db_rule.conditions)
        base_prob = db_rule.action['value']
        min_threshold = db_rule.action.get('min_threshold', 0.0)

        def rule_method(self, symptom=MATCH.symptom, present=MATCH.present):
            """Метод правила с динамической проверкой"""
            # 1. Собираем все текущие симптомы
            current_symptoms = {
                fact['symptom'].lower(): fact['present']
                for fact in self.facts.values()
                if isinstance(fact, SymptomFact)
            }
            
            print('\nТекущие симптомы:', current_symptoms)
            print(f"Проверяем правило для: {disease_name}")

            # 2. Подсчет совпадений с условиями правила
            matched = sum(
                1 for cond in db_rule.conditions
                if cond['symptom'].lower() in current_symptoms
                and current_symptoms[cond['symptom'].lower()] == cond['present']
            )
            
            print(f"Совпадений: {matched}/{total_symptoms} (порог: {min_threshold})")

            # 3. Проверка порога
            if matched / total_symptoms < min_threshold:
                print(f"Порог не пройден: {matched}/{total_symptoms} < {min_threshold}")
                return

            # 4. Расчет вероятности
            probability = (matched / total_symptoms) * base_prob
            print(f"Рассчитанная вероятность: {probability:.1f}%")

            # 5. Обновление заболевания
            for fact in self.facts.values():
                if isinstance(fact, DiseaseFact) and fact['name'] == disease_name:
                    self.modify(fact, 
                              probability=round(probability, 1),
                              matched_symptoms=matched,
                              total_symptoms=total_symptoms)
                    print(f"=== Применено: {disease_name} {probability:.1f}% ===")
                    break

        # Создаем правило, которое активируется для любого симптома,
        # но проверяет принадлежность к симптомам этого правила
        rule = Rule(
            SymptomFact(
                symptom=MATCH.symptom,
                present=MATCH.present
            ),
            TEST(lambda symptom: symptom in rule_symptoms)
        )(rule_method)

        # Регистрируем правило с уникальным именем
        rule_name = f"rule_{db_rule.id}_{disease_name}"
        setattr(self.__class__, rule_name, rule)
