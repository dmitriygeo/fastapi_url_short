
## Запуск тестов

Установка необходимых зависимостей
```bash
pip install pytest pytest-cov locust
```

### Юнит-тесты


1. Запуск юнит-тестов:
```bash
pytest tests/unit_test.py
```

2. Запуск с подробным выводом:
```bash
pytest -v tests/unit_test.py
```

3. Запуск с отчетом о покрытии:
```bash
coverage run -m pytest tests
coverage report -m
coverage html
```


### Нагрузочные тесты

1. Запустите Locust:
```bash
locust -f tests/lock_test.py
```

2. Откройте веб-интерфейс Locust в браузере http://localhost:8089, чтобы настроить параметры нагрузночного тестирования и посмотреть результаты
