# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 0 — Project Initialization)

---

## 1. Текущий STEP

**STEP 0 — Project Initialization — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `7cf5f72 chore: STEP 0 — project initialization`
- Статус: полностью восстановляем, готов к STEP 1

**Последний завершённый STEP:** STEP 0 (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 1 — Foundation (см. §15)

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |

> Ориентировочный план (из протокола, может меняться — фиксируется здесь):
> 0 Initialization ✅ → 1 Foundation → 2 Database → 3 Authentication → 4 Profiles → 5 Posts & Media → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Vite] → [Backend API: FastAPI] → [PostgreSQL + Storage]
                     ↕ i18n (ru/kk/en)        ↕ JWT HttpOnly Cookie
                     ↕ TanStack Query         ↕ SQLAlchemy 2.x + Alembic
```

- Frontend: план — `frontend/src/{pages,components,features,api,hooks,lib,stores,locales,types}` + shadcn/ui + i18next (ru/kk/en) + TanStack Query
- Backend: план — `backend/app/{main,core,config,database,models,schemas,api/v1,services,middleware,tests}` + Alembic
- Database: план — PostgreSQL (prod: Neon/Supabase, dev: Docker), SQLAlchemy 2.x
- Детали → `ARCHITECTURE.md`

---

## 4. Frontend Status

- Статус: **scaffold placeholder** (STEP 0)
- Созданы: `frontend/src/locales/{ru,kk,en}.json` с базовыми ключами, пустые директории `api, components/ui, features, pages, hooks, lib, stores, types`
- Vite/React/TS/Tailwind: **не установлены** (будет в STEP 1)
- Build: не проверялся (нет кода)
- i18n: ключи заготовлены, провайдер — в STEP 1
- Theme: план — light/dark/system

---

## 5. Backend Status

- Статус: **scaffold placeholder** (STEP 0)
- Созданы: `backend/app/__init__.py`, пустые `core, database, models, schemas, api/v1, services, tests`, `backend/alembic/`
- FastAPI/SQLAlchemy: **не установлены** (будет в STEP 1)
- `main.py` / `core/config.py` / `/health`: нет (STEP 1)
- Build/startup: не проверялся (нет кода)

---

## 6. Database Status

- Статус: **не создана**
- Engine: не настроен
- Migrations: 0
- Seed data: нет

План STEP 1-2: поднять PostgreSQL (Docker) или SQLite fallback, модель `users`, первая миграция.

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| — | (нет) | — | — |

---

## 8. Authentication Status

- Статус: **не реализовано** (план STEP 3)
- План: Argon2id + JWT (access 15m + refresh 7d) в `HttpOnly+Secure+SameSite=Lax` cookies + CSRF + `GET /auth/me`
- Hashing / tokens / cookies / CSRF / rate limit: planned

---

## 9. Implemented Features

> STEP 0 — только scaffolding, features не реализованы.

- [ ] Auth (register/login/logout/me)
- [ ] Profiles (avatar, bio, skills, links)
- [ ] Posts + media + hashtags/mentions
- [ ] Feed (cursor pagination)
- [ ] Post interactions (like, comment, repost, bookmark, follow)
- [ ] Stories (24h)
- [ ] Clubs + channels + roles
- [ ] Messaging (DM + club)
- [ ] Notifications
- [ ] Search (users/posts/clubs/hashtags)
- [ ] Projects showcase
- [ ] i18n (ru/kk/en)
- [ ] Dark/Light theme

---

## 10. Deployment Status

- Frontend hosting: не выбран (кандидат: Vercel)
- Backend hosting: не выбран (кандидат: Render / Railway / Fly.io)
- Database hosting: не выбран (кандидат: Neon / Supabase)
- Domain: нет
- CI/CD: нет
- Prod env vars: не настроены
- URL: нет

---

## 11. Tests Status

- Backend tests: 0 (`backend/app/tests/` пуст)
- Frontend tests: 0
- Coverage: —
- Последние запуски: нет (нет кода)

---

## 12. Known Issues

- Нет известных багов — кода ещё нет (STEP 0).
- Решение по storage (local FS vs S3/R2) отложено до STEP 2/3.
- E2EE отложено (MASTER_PROMPT §21) — не реализовывать без качественной криптографии.

---

## 13. Technical Debt

- Нет (чистый старт). Долг будет фиксироваться начиная с STEP 1.

---

## 14. Current Blockers

- Нет блокеров. Ожидается команда на STEP 1.

---

## 15. Next Recommended STEP

**STEP 1 — Foundation**

Цель: runnable scaffold, который можно запустить и проверить.

Нужно сделать:
1. Инициализировать `frontend` (Vite + React + TS + Tailwind + shadcn + i18next + React Router + TanStack Query)
2. Инициализировать `backend` (FastAPI + SQLAlchemy + Pydantic + Alembic + argon2 + JWT, `main.py` + `/health` + `/api/v1/auth` skeleton)
3. `docker-compose.yml` для Postgres (опционально) + `.env` wiring
4. Проверка: `npm run dev` + `uvicorn app.main:app --reload` + `npm run build` + `pytest` (smoke)

После STEP 1: обновить этот файл + `DEVELOPMENT_LOG.md` + `ARCHITECTURE.md` если будут изменения.

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Stack: React+TS+Vite+Tailwind+shadcn / FastAPI+SQLAlchemy+PostgreSQL | MASTER_PROMPT §8-9 |
| 2026-09-05 | Auth: Argon2id + HttpOnly cookies (access+refresh) | Security §11 |
| 2026-09-05 | i18n с localStorage + browser fallback | 3 языка §5 |
| 2026-09-05 | Cursor pagination для feed | §15 |
| 2026-09-05 | Protocol: PROJECT_STATE = оперативная память, DEVELOPMENT_LOG = история, MASTER_PROMPT = source of truth | Persistent Protocol 2026-09-05 |
| 2026-09-05 | STEP tracking: 0..17 ориентировочно, может делиться/объединяться с фиксацией | Persistent Protocol §3 |

---

## 17. Последний Git Commit

```
7cf5f72 chore: STEP 0 — project initialization (workspace, docs, structure, git) — 2026-09-05
Branch: main | Status: clean | Remote: не настроен
Файлы: .env.example, .gitignore, ARCHITECTURE.md, MASTER_PROMPT.md, PROJECT_STATE.md, README.md, SECURITY.md, backend/app/__init__.py, docs/MASTER_PROMPT.md, frontend/src/locales/{ru,kk,en}.json
```

---

## 18. Изменённые файлы (STEP 0)

```
Bailanysta/
├── MASTER_PROMPT.md
├── PROJECT_STATE.md        ← этот файл
├── ARCHITECTURE.md
├── SECURITY.md
├── README.md
├── DEVELOPMENT_LOG.md      ← создан в протоколе 2026-09-05
├── .gitignore
├── .env.example
├── docs/MASTER_PROMPT.md
├── frontend/src/locales/{ru,kk,en}.json
├── frontend/src/{api,components/ui,features,pages,hooks,lib,stores,types}/
└── backend/{app/{core,database,models,schemas,api/v1,services,tests},alembic}/
```

---

## 19. Как восстанавливать контекст (New Chat Recovery)

1. Найти workspace `C:\Users\lueex\Desktop\Bailanysta`
2. Прочитать `MASTER_PROMPT.md` (source of truth)
3. Прочитать этот `PROJECT_STATE.md` (текущее состояние)
4. Прочитать `ARCHITECTURE.md` + `SECURITY.md`
5. Прочитать последние записи `DEVELOPMENT_LOG.md`
6. Проверить `git status` + `git log --oneline -5`
7. Проверить структуру `frontend/` и `backend/`
8. Определить последний завершённый STEP и следующий

→ Сообщить краткое состояние и ждать команды, не начинать STEP автоматически.
