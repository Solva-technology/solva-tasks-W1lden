# 📝 PyTask — менеджер задач с интеграцией Telegram

Сервис для управления учебными задачами и группами студентов.
Поддерживает роли (студент, админ, преподаватель, менеджер), постановку и отслеживание задач с дедлайнами, а также автоматические уведомления в Telegram. 

---

## 🧱 Стек технологий

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Docker + Docker Compose
- Pytest + Ruff + GitHub Actions
- Telegram Bot API (webhook)

---

## 🗂 Структура проекта

```

solva-tasks-W1lden/
├─ src/
│  ├─ migrations/
│  │  ├─ versions/
│  │  │  ├─ 6fa6f4e20f9e_deadline_notice.py
│  │  │  ├─ 75c15102f0a5_add_teacher_to_group.py
│  │  │  └─ b85f64aef513_init.py
│  │  ├─ env.py
│  │  ├─ README
│  │  └─ script.py.mako
│  ├─ tasks/
│  │  ├─ api/
│  │  │  ├─ endpoints/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ auth.py
│  │  │  │  ├─ groups.py
│  │  │  │  ├─ tasks.py
│  │  │  │  ├─ telegram.py
│  │  │  │  └─ users.py
│  │  │  ├─ schemas/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ auth.py
│  │  │  │  ├─ group.py
│  │  │  │  ├─ task.py
│  │  │  │  └─ user.py
│  │  │  ├─ deps.py
│  │  │  └─ routers.py
│  │  ├─ core/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py
│  │  │  ├─ config.py
│  │  │  ├─ constants.py
│  │  │  ├─ db.py
│  │  │  ├─ enums.py
│  │  │  └─ security.py
│  │  ├─ db/
│  │  │  ├─ crud/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ group.py
│  │  │  │  ├─ task.py
│  │  │  │  └─ user.py
│  │  │  └─ models/
│  │  │     ├─ __init__.py
│  │  │     ├─ group.py
│  │  │     ├─ task.py
│  │  │     └─ user.py
│  │  ├─ logs/
│  │  ├─ services/
│  │  │  ├─ __init__.py
│  │  │  ├─ logger.py
│  │  │  ├─ scheduler.py
│  │  │  └─ telegram.py
│  │  ├─ tests/
│  │  │  ├─ __init__.py
│  │  │  ├─ conftest.py
│  │  │  ├─ test_auth.py
│  │  │  ├─ test_groups.py
│  │  │  ├─ test_notifications.py
│  │  │  ├─ test_permissions.py
│  │  │  ├─ test_task_teacher.py
│  │  │  ├─ test_tasks.py
│  │  │  ├─ test_user.py
│  │  │  └─ test_webhook.py
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ alembic.ini
│  ├─ Dockerfile
│  └─ requirements.txt
├─ tasks/
│  └─ logs/
├─ .env
├─ .gitignore
├─ docker-compose.yml
├─ pytest.ini
├─ README.md
├─ ruff.toml
└─ test.db


```

---

## 🚀 Запуск проекта

1. Клонируйте репозиторий:
```bash
https://github.com/W1lden/PyTasks.git
```

2. Создайте .env файл в каталоге src. Вот пример:
```env_example
APP_TITLE="PyTasks"
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
JWT_SECRET=change_this_secret_please
JWT_ALG=HS256
TELEGRAM_BOT_TOKEN=8259991608:AAHyJe5mJ58B_kueqHkQ3EWdLsVpRoaNcoQ
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
ENABLE_SCHEDULER=true

PUBLIC_BASE_URL=https://33732eda6ea7.ngrok-free.app
TELEGRAM_WEBHOOK_PATH=/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=abc123supersecretxyz

```
5. В браузере прейдите на страницу документации:
```bash
http://0.0.0.0:8000/docs
```

---



## 🌐 Ручки

🔑 Auth

POST /auth/telegram/callback
Регистрация или авторизация пользователя через Telegram (по telegram_id, username, full_name).
Возвращает access_token.

GET /users/me
Информация о текущем пользователе (на основе JWT).

👥 Users

GET /users/me
Данные авторизованного пользователя.

PUT /users/{user_id}/role (ADMIN)
Изменить роль пользователя (student / teacher / manager / admin).

👩‍🏫 Groups

POST /groups/ (ADMIN, TEACHER)
Создать учебную группу (с указанием преподавателя и менеджера).

GET /groups/
Список групп с участниками.

GET /groups/{group_id}
Детали конкретной группы.

POST /groups/{group_id}/add_student?student_id=... (ADMIN, TEACHER)
Добавить студента в группу.

✅ Tasks

POST /tasks/ (TEACHER, ADMIN)
Создать задачу для студента с дедлайном.

GET /tasks/
Список задач (фильтрация по student_id, group_id, status, пагинация).

GET /tasks/{task_id}
Получить задачу по ID.

PATCH /tasks/{task_id} (STUDENT)
Изменить статус своей задачи (например, «сдана»).

🔔 Notifications

Уведомления отправляются в Telegram студенту, менеджеру и преподавателю:

при создании задачи;

при изменении её статуса;

при просрочке дедлайна.

---

## 👤 Автор

[W1lden (GitHub)](https://github.com/W1lden)
