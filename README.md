# API-сервис сокращения ссылок
Сервис для сокращения URL-адресов с использованием FastAPI, PostgreSQL и Redis. Ссылка на сервис: https://fastapi-url-short-1.onrender.com

## Аутентификация
- `POST /api/v1/users/` - Регистрация нового пользователя
- `POST /api/v1/token` - Получение JWT токена

### Управление ссылками
- `POST /api/v1/links/shorten` - Создание короткой ссылки
- `GET /{short_code}` - Переход по короткой ссылке
- `GET /api/v1/links/{short_code}/stats` - Получение статистики ссылки
- `PUT /api/v1/links/{short_code}` - Обновление ссылки (только для создателя ссылки)
- `DELETE /api/v1/links/{short_code}` - Удаление ссылки (только для создателя ссылки)

- ## Примеры запросов

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password"
     }'
```

### Получение токена
```bash
curl -X POST "http://localhost:8000/api/v1/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=password"
```

### Создание короткой ссылки
```bash
curl -X POST "http://localhost:8000/api/v1/links/shorten" \
     -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{
       "original_url": "https://example.com/very/long/url",
       "custom_alias": "mylink",
       "expires_at": "2025-03-24T08:44:26.784Z"
     }'
```


## База данных

### Таблица users
id - уникальный индентификатор пользователя;

email - уникальный Email пользователя;

hashed_password - хэшированный пароль;

is_active - статус пользователя;

created_at - дата и время создания аккаунта;

updated_at - дата и время обновления аккаунта;


### Таблица links

id - уникальный индентификатор ссылки;

original_url - оригинальный url;

short_code - сгенерированный короткий код;

custom_alias - пользовательский алиас;

expires_at - дата и время истечения срока действия;

created_at - дата и время создания ссылки;

updated_at - дата и время последнего обновления;

last_accessed - Дата и время последнего доступа;

access_count - Количество переходов по ссылке;

user_id - кнешний ключ на таблицу users;


### Установка с помощью Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/dmitriygeo/fastapi_url_short.git
cd fastapi_url_short
```

2. Создайте файл .env:
```env
POSTGRES_SERVER
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
REDIS_HOST
REDIS_PORT
SECRET_KEY
```

3. Запустите с помощью Docker:
```bash
docker build -t url-shortener .
docker run -d \
  --name url-shortener \
  -p 8000:8000 \
  --env-file .env \
  url-shortener
```

### Локальная установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Примените миграции:
```bash
alembic upgrade head
```

4. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

