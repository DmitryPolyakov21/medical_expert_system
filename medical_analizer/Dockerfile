FROM python:3.11-alpine

RUN apk add --no-cache curl

# Устанавливаем системные зависимости для psycopg2
RUN apk add --no-cache python3-dev musl-dev

# Обновляем pip и устанавливаем пакеты
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Создаём и переключаемся в рабочую директорию
WORKDIR /app

# 3. Копируем зависимости
COPY requirements.txt .

# 4. Устанавливаем Python-пакеты
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь проект
COPY . .

# 6. Запускаем сервер (команда может быть другой)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
