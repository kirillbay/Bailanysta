# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после каждого STEP.
> Последнее обновление: 2026-09-05 (STEP 0 — Project Initialization)

---

## 1. Текущий этап

**STEP 0 — Project Initialization — ЗАВЕРШЁН**

- Workspace создан: `C:\Users\lueex\Desktop\Bailanysta`
- MASTER_PROMPT сохранён
- Архитектура определена (ARCHITECTURE.md)
- Security principles зафиксированы (SECURITY.md)
- Git инициализирован
- Базовая структура проекта создана
- Ожидается команда на STEP 1

**Next Step:** STEP 1 — Foundation (Backend scaffold + Frontend scaffold + Auth skeleton) — ожидает указания.

---

## 2. Завершённые этапы

| STEP | Название | Дата | Статус | Кратко |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | ✅ Done | Workspace, docs, git, env, architecture |

---

## 3. Текущая архитектура

### Общая схема

```
[Browser] → [Frontend: React + Vite] → [Backend API: FastAPI] → [PostgreSQL + Storage]
                     ↕ i18n (ru/kk/en)        ↕ JWT HttpOnly Cookie
                     ↕ TanStack Query         ↕ SQLAlchemy 2.x + Alembic
```

### Frontend (план)

- `frontend/` — Vite + React + TypeScript
- `frontend/src/pages/` — route pages
- `frontend/src/components/` — shared + ui (shadcn)
- `frontend/src/features/` — domain features (auth, feed, posts, clubs...)
- `frontend/src/api/` — API clients
- `frontend/src/hooks/`, `lib/`, `stores/`, `types/`, `locales/`
- i18n: `i18next` + `react-i18next`, `frontend/src/locales/{ru,kk,en}.json`
- State: TanStack Query (server), Zustand/Context (client)

### Backend (план)

- `backend/app/` — FastAPI app
- `backend/app/main.py` — entrypoint
- `backend/app/core/` — config, security
- `backend/app/database/` — engine, session, Base
- `backend/app/models/` — SQLAlchemy models
- `backend/app/schemas/` — Pydantic schemas
- `backend/app/api/v1/` — routers
- `backend/app/services/`, `repositories/`, `middleware/`, `tests/`
- Migrations: `backend/alembic/`

### Database (план)

- Production: PostgreSQL (managed: Neon / Supabase / Railway)
- Dev: PostgreSQL (Docker) с fallback на SQLite для быстрых тестов
- ORM: SQLAlchemy 2.x async/sync (решение в STEP 1)

---

## 4. Созданные features

> На STEP 0 — features не реализованы, только scaffolding.

- [ ] Auth (register/login/logout/me)
- [ ] Profiles
- [ ] Posts + interactions
- [ ] Feed (pagination)
- [ ] Stories
- [ ] Clubs + channels
- [ ] Messaging (DM + club messages)
- [ ] Notifications
- [ ] Search
- [ ] Projects showcase
- [ ] Bookmarks
- [ ] i18n (ru/kk/en)
- [ ] Dark/Light theme

---

## 5. Изменённые файлы (STEP 0)

```
Bailanysta/
├── MASTER_PROMPT.md
├── PROJECT_STATE.md        ← этот файл
├── ARCHITECTURE.md
├── SECURITY.md
├── README.md
├── .gitignore
├── .env.example
├── docs/
│   └── MASTER_PROMPT.md    ← копия (опционально)
├── frontend/               ← пустая структура, scaffold в STEP 1
│   ├── src/
│   │   ├── locales/        ← i18n placeholder
│   │   └── ...
├── backend/                ← пустая структура, scaffold в STEP 1
│   └── app/
└── ...
```

---

## 6. Database status

- Статус: не создана (ожидает STEP 1)
- Engine: не настроен
- Migrations: 0
- Seed data: нет

**План на STEP 1:**
- Поднять PostgreSQL (Docker) или подготовить SQLite fallback
- Создать модель `users`
- Настроить Alembic
- Первая миграция `init`

---

## 7. Migrations

| Revision | Description | Date |
|----------|-------------|------|
| — | (нет) | — |

---

## 8. Tests

- Backend tests: 0 (запуск в STEP 1)
- Frontend tests: 0
- Coverage: —

---

## 9. Known issues / Ограничения

- STEP 0 — инициализация, известных багов нет (кода ещё нет).
- Решение по хранению uploads (local FS vs S3) будет принято в STEP 2/3.
- E2EE отложено (см. MASTER_PROMPT §21) — не реализовывать без качественной криптографии.

---

## 10. Deployment status

- Frontend hosting: не выбран (кандидаты: Vercel / Netlify)
- Backend hosting: не выбран (кандидаты: Render / Railway / Fly.io)
- Database hosting: не выбран (кандидаты: Neon / Supabase)
- Domain: нет
- CI/CD: нет
- Env vars production: не настроены

---

## 11. Технические решения (принятые в STEP 0)

| Решение | Выбор | Причина |
|---------|-------|---------|
| Frontend stack | React + TS + Vite + Tailwind + shadcn + TanStack Query + RHF + Zod + i18next | Рекомендован в MASTER_PROMPT §8, современный, быстрый |
| Backend stack | Python + FastAPI + SQLAlchemy 2.x + Pydantic + Alembic + PostgreSQL | §9 — асинхронность, типизация, скорость |
| Auth | Argon2id + HttpOnly Secure SameSite cookies + JWT (access+refresh) | §11 — безопасность |
| i18n | i18next с сохранением в localStorage + browser detection | §5 — три языка |
| Pagination | cursor-based для feed | §15 |
| File storage | Локально в dev, S3-совместимое в prod (абстракция) | §32 |

---

## 12. TODO (до STEP 1)

- [x] Создать workspace
- [x] Сохранить MASTER_PROMPT
- [x] Создать docs
- [x] Создать .gitignore / .env.example
- [x] Инициализировать Git
- [ ] STEP 1: Scaffold frontend (Vite) + backend (FastAPI) + проверка запуска

---

## 13. Логи изменений

- **2026-09-05** — STEP 0 выполнен. Созданы все базовые документы, структура, git.

---

## 14. Как восстанавливать контекст

1. Прочитай `MASTER_PROMPT.md` (полный source of truth)
2. Прочитай этот `PROJECT_STATE.md` (текущий снимок)
3. Прочитай `ARCHITECTURE.md` (технические детали)
4. Прочитай `SECURITY.md` (security checklist)
5. Осмотри `frontend/` и `backend/` — что уже реализовано
6. Проверь `git log` и `git status`
