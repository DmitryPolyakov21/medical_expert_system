import os
from datetime import datetime

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Получаем путь из переменных окружения
        self.log_path = os.getenv('DJANGO_LOG_PATH', '/var/log/django/requests.log')
        
        # Создаем директорию если нет
        log_dir = os.path.dirname(self.log_path)
        os.makedirs(log_dir, exist_ok=True)

    def __call__(self, request):
        # Логирование перед обработкой запроса
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {request.META.get('REMOTE_ADDR')} - {request.method} {request.path}\n"
        
        with open(self.log_path, 'a') as f:
            f.write(log_entry)

        response = self.get_response(request)
        return response
