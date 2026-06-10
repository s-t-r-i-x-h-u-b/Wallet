# Образ для непрерывной интеграции (CI): модульные/интеграционные тесты с
# покрытием, статический анализ безопасности (Bandit, SAST) и проверка
# зависимостей (pip-audit, SCA).
#
# GUI-зависимости (kivy, kivymd) намеренно не устанавливаются: слой
# представления не покрывается юнит-тестами, а тесты ядра и сервисов от него
# не зависят. Это делает образ лёгким и быстрым.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

# Зависимости, необходимые для тестов ядра/сервисов и инструментов качества
RUN pip install --no-cache-dir \
    pycryptodome matplotlib \
    pytest pytest-cov bandit pip-audit

COPY . .

# Контроль качества: тесты с покрытием -> SAST -> SCA
CMD ["sh", "-c", \
     "pytest --cov=wallet --cov-report=term-missing && \
      bandit -r wallet && \
      pip-audit -r requirements.txt"]
