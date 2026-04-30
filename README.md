# HH Killer — Веб-платформа вакансий

## 🚀 Быстрый старт

### 1. Создать виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate      # Windows
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Загрузить навыки
```bash
python manage.py loaddata users/fixtures/skills.json
```

### 5. Создать суперпользователя (администратор)
```bash
python manage.py createsuperuser
```

### 6. Запустить сервер
```bash
python manage.py runserver
```

Сайт доступен по адресу: **http://127.0.0.1:8000**

---

## 📂 Структура проекта

```
hh-killer/
├── config/          # Настройки Django
├── users/           # Пользователи, профили, навыки
├── jobs/            # Вакансии, отклики, matching
├── support/         # Служба поддержки
├── templates/       # HTML-шаблоны
├── static/          # CSS и JS
└── manage.py
```

## 🎯 Алгоритм подбора (Matching)

Система сравнивает навыки соискателя с требованиями вакансии:
- 7 из 10 навыков совпало → **70%**
- Вакансии сортируются по убыванию совпадения
- Работодатели видят подходящих кандидатов

## 🔑 Роли пользователей

| Роль | Возможности |
|------|-------------|
| **Соискатель** | Профиль, навыки, отклики, рекомендации, избранное |
| **Работодатель** | Создание вакансий, просмотр откликов, поиск кандидатов |
| **Администратор** | Django Admin + панель поддержки |

## ⚙️ PostgreSQL (опционально)

Создайте `.env` файл:
```
USE_POSTGRES=True
DB_NAME=hh_killer
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```
