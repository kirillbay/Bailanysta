# Bailanysta — DEVELOPMENT LOG

> Исторический журнал разработки. Каждая запись — один STEP.
> PROJECT_STATE.md — оперативная память; этот файл — история.
> Формат записи определён в PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05).

---

## STEP 0 — Project Initialization

### Date

2026-09-05

### Objective

Создать рабочее пространство проекта, зафиксировать продуктовый контекст, подготовить архитектурный план и базовую документацию. НЕ начинать массовую реализацию функциональности (MASTER_PROMPT §65).

Задачи по MASTER_PROMPT §65:
1. Создать `Desktop/Bailanysta`
2. Инициализировать Git
3. Создать базовую структуру проекта
4. Сохранить MASTER_PROMPT.md
5. Создать PROJECT_STATE.md, ARCHITECTURE.md, SECURITY.md, README.md, .gitignore, .env.example
6. Определить первоначальную архитектуру frontend/backend
7. Проверить структуру и Git, остановиться и ждать STEP 1

### Implemented

- Создана директория `C:\Users\lueex\Desktop\Bailanysta` с подструктурой:
  - `frontend/src/{locales,components/ui,pages,api,features,hooks,lib,stores,types}`
  - `backend/{app/{core,database,models,schemas,api/v1,services,tests},alembic}`
  - `docs/`
- Сохранён `MASTER_PROMPT.md` (корень, 68 секций) + копия `docs/MASTER_PROMPT.md`
- Создан `PROJECT_STATE.md` — persistent memory с текущим этапом, архитектурой, планами DB/migrations/tests/deployment
- Создан `ARCHITECTURE.md` — high-level схема, frontend/backend stack, API design `/api/v1/*`, DB entities поэтапно, auth, uploads, realtime, i18n, performance, deployment, trade-offs
- Создан `SECURITY.md` — auth/session, authorization, validation/injection, file upload, CORS/headers, secrets, abuse protection, privacy/E2EE checklist
- Создан `README.md` — overview, features, tech stack, architecture diagram, project structure, quick start (after STEP 1), env vars, deployment, design, security, roadmap
- Создан `.gitignore` — secrets, Python/Node/OS/IDE артефакты
- Создан `.env.example` — все ключевые переменные без секретов (DATABASE_URL, SECRET_KEY, CORS, VITE_API_URL, storage)
- Созданы i18n заготовки: `frontend/src/locales/{ru.json,kk.json,en.json}` с ключами `common/nav/auth/post`
- Инициализирован Git (`main` branch, user `Kirill - Bailanysta`), первый commit `7cf5f72`
- Добавлен `docs/README.md` и `backend/app/__init__.py` как маркеры структуры

### Files Changed

```
[new] MASTER_PROMPT.md
[new] PROJECT_STATE.md
[new] ARCHITECTURE.md
[new] SECURITY.md
[new] README.md
[new] DEVELOPMENT_LOG.md        ← создан в рамках Persistent Protocol (2026-09-05, второй частью STEP 0)
[new] .gitignore
[new] .env.example
[new] docs/MASTER_PROMPT.md
[new] docs/README.md
[new] backend/app/__init__.py
[new] frontend/src/locales/ru.json
[new] frontend/src/locales/kk.json
[new] frontend/src/locales/en.json
[dirs] frontend/src/{api,components/ui,features,pages,hooks,lib,stores,types}
[dirs] backend/{app/{core,database,models,schemas,api/v1,services,tests},alembic}
```

Обновления в рамках Persistent Protocol (тот же день, продолжение STEP 0):
- `PROJECT_STATE.md` расширен до формата протокола (§1 — 19 секций: текущий STEP, список STEP, frontend/backend/database/migrations/auth/features/deployment/tests/known issues/debt/blockers/next step/decisions/last commit)
- `DEVELOPMENT_LOG.md` создан с этой записью

### Database Changes

Нет. DB не создана (план STEP 1-2). Migrations: 0.

### API Changes

Нет. API не реализован (план STEP 1 — `GET /health`, `POST /auth/*` skeleton).

### Frontend Changes

Только scaffolding:
- i18n JSON с базовыми строками (ru/kk/en)
- Пустые директории под будущие модули

Vite/React/Tailwind/shadcn — не установлены (STEP 1).

### Security Changes

Зафиксированы принципы в `SECURITY.md`:
- Argon2id + HttpOnly Secure SameSite cookies + JWT (access 15m / refresh 7d)
- Backend authorization, validation, IDOR prevention, upload checks, CORS, rate limit, headers

Реализации пока нет — только план.

### Tests

- Backend: 0 tests, не запускались (нет кода)
- Frontend: 0 tests
- Проверок build: нет (нет runnable кода)

### Build

- `npm run dev` / `npm run build`: не проверялись — frontend ещё не инициализирован (STEP 1)
- `uvicorn app.main:app --reload`: не проверялся — backend ещё не инициализирован
- Структура директорий verified via `Get-ChildItem`

### Problems

Нет критических проблем. STEP 0 — только инициализация.

Замечания:
- `frontend` и `backend` — пустые scaffolds, любой импорт упадёт до STEP 1 (ожидаемо)
- Remote Git (GitHub) не настроен — будет в STEP 16 (Deployment)

### Fixed

Нет фиксов — первый STEP.

### Known Issues

- Нет runnable приложения до STEP 1
- Storage decision (local vs S3/R2) отложен
- E2EE отложено сознательно (§21 MASTER_PROMPT)

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| Frontend | React + TS + Vite + Tailwind + shadcn + TanStack Query + RHF + Zod + i18next | MASTER_PROMPT §8 |
| Backend | Python + FastAPI + SQLAlchemy 2.x + Pydantic + Alembic + PostgreSQL | §9 |
| Auth | Argon2id + JWT cookies HttpOnly Secure SameSite | §11 + SECURITY.md |
| Pagination | cursor-based для feed | §15 |
| Storage | local dev / S3 abstraction prod | §32 |
| Docs split | MASTER_PROMPT (что/почему) / PROJECT_STATE (где сейчас) / DEVELOPMENT_LOG (как пришли) | Persistent Protocol §9 |

### Next Step

**STEP 1 — Foundation**

- Scaffold `frontend` (Vite) + `backend` (FastAPI) до runnable состояния
- `GET /health`, `GET /api/v1/auth/me` skeleton
- `docker-compose.yml` для Postgres (опционально)
- Проверки: frontend build + backend startup + smoke tests
- После — обновить PROJECT_STATE.md + DEVELOPMENT_LOG.md + git commit

> Примечание: Persistent Development Protocol (получен 2026-09-05) принят как обязательный для всех будущих STEP. Настоящая запись дополнена им в тот же день без отдельного STEP.

---

## STEP 1 — Foundation

### Date

2026-09-05

### Objective

Превратить каркас в реально запускаемый foundation: связать frontend + backend + API, настроить routing, API client, application shell, health check, базовую обработку ошибок, environment, i18n, theme, responsive, проверки сборки/типов. Без бизнес-функций (auth/posts/clubs и т.д. — отдельные STEP).

### Implemented

**Frontend:**
- `package.json` — React 18 + Vite 6 + TS 5.6 + Tailwind 3 + shadcn-like ui + Lucide + React Router 6 + TanStack Query 5 + RHF + Zod + i18next 24 (+ @types/node)
- Config: `vite.config.ts` (alias @, ports 5173/4173), `tsconfig.json` + `tsconfig.node.json` (composite), `tailwind.config.js` (CSS variables, darkMode class, radius), `postcss.config.js`, `index.html`, `src/vite-env.d.ts`
- Core: `src/lib/utils.ts` (cn), `src/lib/i18n.ts` (resources ru/kk/en, detector localStorage→navigator, persistence), `src/api/client.ts` (fetch wrapper, VITE_API_URL, ApiError, health()), `src/hooks/useHealth.ts` (useQuery), `src/stores/theme.tsx` (light/dark/system + localStorage + matchMedia), `src/components/ErrorBoundary.tsx`
- UI: `components/ui/button.tsx`, `card.tsx`, `badge.tsx`, `skeleton.tsx` — rounded-2xl, border, shadow-sm
- Layout: `components/layout/AppShell.tsx` — Sidebar (260px, desktop) с логотипом Б, 9 nav items, LanguageSwitcher (RU/KZ/EN), ThemeSwitcher, BottomNav (mobile 5 items), TopBar (mobile), responsive shell с `Outlet`
- Pages: `pages/FeedPage.tsx` — hero (Байланыста болайық), 3 карточки Threads/Discord/GitHub, health-check card (loading/success/error с ApiError, refetch), skeleton + empty demo; `pages/PlaceholderPage.tsx` — заглушка с Badge STEP 1; `pages/NotFoundPage.tsx` — 404
- Routing: `src/App.tsx` — `createBrowserRouter` с 9 маршрутами (`/`, `/explore`, `/search`, `/clubs`, `/projects`, `/messages`, `/notifications`, `/profile`, `/settings`, `*` → 404) под `AppShell`
- Entry: `src/main.tsx` — QueryClient (retry 1, stale 30s), ThemeProvider, ErrorBoundary, i18n import; `src/index.css` — Tailwind base + CSS vars light/dark
- i18n: подключён, переключатель в Sidebar, все nav через `t()`

**Backend:**
- `requirements.txt` — fastapi 0.115.6, uvicorn[standard] 0.34, pydantic 2.10, pydantic-settings 2.7, sqlalchemy 2.0.36, alembic 1.14, httpx, pytest, anyio
- `app/core/config.py` — BaseSettings (env_file .env, cors_origins string→list, is_production, database_url placeholder sqlite)
- `app/api/v1/health.py` — `GET /health` → `{status,service,version,env}`
- `app/api/v1/router.py` — агрегатор
- `app/main.py` — FastAPI (title Bailanysta), CORSMiddleware (allow_origins from settings, credentials true), security headers middleware (nosniff, DENY, Referrer-Policy, HSTS в prod), global exception handler (500 без stack trace), routers (`/api/v1` + `/health` + `/`)
- `app/database/base.py` — placeholder (STEP 2)
- `pytest.ini` + `app/tests/test_health.py` — 6 тестов (root, v1 health, CORS, headers, 404)

**Env:**
- `.env.example` уже существовал, `VITE_API_URL=http://localhost:8000` используется в `api/client.ts`; backend `CORS_ORIGINS=http://localhost:5173,http://localhost:3000` — корректно
- Никаких секретов в frontend bundle (только VITE_)

### Files Changed

```
[new] frontend/package.json
[new] frontend/index.html
[new] frontend/vite.config.ts
[new] frontend/tsconfig.json
[new] frontend/tsconfig.node.json
[new] frontend/tailwind.config.js
[new] frontend/postcss.config.js
[new] frontend/src/main.tsx
[new] frontend/src/App.tsx
[new] frontend/src/vite-env.d.ts
[new] frontend/src/index.css
[new] frontend/src/lib/utils.ts
[new] frontend/src/lib/i18n.ts
[new] frontend/src/api/client.ts
[new] frontend/src/hooks/useHealth.ts
[new] frontend/src/stores/theme.tsx
[new] frontend/src/components/ErrorBoundary.tsx
[new] frontend/src/components/ui/button.tsx
[new] frontend/src/components/ui/card.tsx
[new] frontend/src/components/ui/badge.tsx
[new] frontend/src/components/ui/skeleton.tsx
[new] frontend/src/components/layout/AppShell.tsx
[new] frontend/src/pages/FeedPage.tsx
[new] frontend/src/pages/PlaceholderPage.tsx
[new] frontend/src/pages/NotFoundPage.tsx
[new] backend/requirements.txt
[new] backend/pytest.ini
[new] backend/app/core/config.py
[new] backend/app/main.py
[new] backend/app/api/v1/health.py
[new] backend/app/api/v1/router.py
[new] backend/app/database/base.py
[new] backend/app/tests/test_health.py
[mod] frontend/tsconfig.node.json — fix composite/allowImportingTsExtensions
[mod] frontend/src/pages/FeedPage.tsx — Badge variant fix
[mod] frontend/src/pages/NotFoundPage.tsx — remove asChild
```

### Database Changes

Нет. DB не создана, migrations 0. SQLAlchemy установлена, но Base/engine — в STEP 2.

### API Changes

- `GET /api/v1/health` → `{status:"ok", service:"Bailanysta", version:"0.1.0", env:"development"}`
- `GET /health` (root, для LB, not in schema)
- `GET /` → `{service, version, docs, health}`
- Все под `settings.api_v1_prefix` (`/api/v1`), JSON, корректные статусы.

### Frontend Changes

Полный scaffold описан в Implemented. Ключевое: routing 9 pages, AppShell responsive, i18n+theme, QueryProvider, ErrorBoundary, health integration (loading/error/empty), production build готов.

### Security Changes

- CORS: allow_origins из env, allow_credentials true, без wildcard `*` с credentials (SECURITY.md §6)
- Security headers: X-Content-Type-Options nosniff, X-Frame-Options DENY, Referrer-Policy, HSTS в prod
- Global exception handler — no stack trace leak
- No secrets in frontend (только VITE_API_URL), .env gitignored
- Validation: пока только health (без input), Pydantic settings — основа для следующих STEP

### Tests

- `npx tsc --noEmit` (frontend) → **PASS** (после fix composite + Badge + NotFound)
- `npm run build` (frontend) → **PASS** — `vite v6.4.3 building... ✓ 1665 modules, dist/index.html 0.68 kB, css 15.29 kB gzip 3.88 kB, js 354.82 kB gzip 113 kB, built in 17.19s`
- `python -c "from app.main import app"` → **import ok**
- `pytest app/tests/test_health.py -v` → **6 passed in 0.76s** (root, health v1, root health, CORS, security headers, 404)
- `curl http://127.0.0.1:8000/api/v1/health` via uvicorn → `{"status":"ok",...}` **OK**
- `curl http://127.0.0.1:8000/` → `{"service":"Bailanysta",...}` **OK**

### Build

- Frontend build: ✅ 17.19s, 354 kB js (113 gzip), 15 kB css
- Backend import: ✅
- Backend tests: ✅ 6/6

### Problems

- `tsconfig` composite error — fixed (composite:true, allowImportingTsExtensions false для node config)
- `Badge variant` type error — fixed (убрал несуществующий variant)
- `Button asChild` type error — fixed (заменил на Link)
- Vite path alias требовал `@types/node` — установлен
- `pip install` warnings про PATH — не критично (user install)

### Fixed

Все выше — исправлено в рамках STEP 1 до зелёных проверок.

### Known Issues

- `npm audit` — 2 moderate (esbuild) — не критично
- Нет `eslint` config (скрипт есть, но не настроен) — low debt
- `version` дублируется в frontend/backend — вынести в single source позже
- Нет `docker-compose.yml` — будет в STEP 2
- Backend `DATABASE_URL` пока sqlite placeholder

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| Fetch vs axios | native fetch | Меньше deps, достаточно, credentials include |
| UI primitives | Вручную button/card/badge/skeleton | Без shadcn CLI, меньше раздувания на STEP 1 |
| Theme | Custom context + localStorage + matchMedia | Без next-themes, проще |
| CORS | string→list property | Совместимо с comma-list в .env |
| Headers middleware | В main.py | SECURITY.md §6, HSTS только prod |
| Routing | createBrowserRouter + AppShell + 9 placeholders | Готово к масштабированию без переделки |

### Next Step

**STEP 2 — Database**

- `app/database/base.py` (Base, engine, session), Alembic init, модель `users` минимально, первая миграция
- `docker-compose.yml` для Postgres (опционально), тесты DB connection
- Обновить PROJECT_STATE.md + DEVELOPMENT_LOG.md

---

## STEP 2 — Database Foundation

### Date

2026-09-05

### Objective

Подготовить production-oriented database foundation: PostgreSQL + SQLAlchemy 2.x + Alembic + User model + docker-compose + health/db, без перехода к auth/posts/clubs. Проверить миграцию, тесты, регрессию STEP1.

### Implemented

**Database config:**
- `backend/requirements.txt` + `psycopg[binary]==3.2.3` + `email-validator==2.2.0` (установлены, `psycopg 3.2.3` verified)
- `backend/app/core/config.py` — `database_url` → `postgresql+psycopg://postgres:postgres@localhost:5432/bailanysta`, добавлен `database_url_safe` (masked), `cors_origins_list`, `is_production`; убран sqlite placeholder

**SQLAlchemy:**
- `backend/app/database/base.py` — `class Base(DeclarativeBase)` (единый metadata для Alembic)
- `backend/app/database/session.py` — `create_engine(settings.database_url, pool_pre_ping=True, echo=debug)`, `SessionLocal = sessionmaker(...)`, `get_db()` yields+close, `check_db_connection()` SELECT 1
- `backend/app/database/__init__.py` + `backend/app/database.py` re-export (удобство `from app.database import Base, get_db`)

**User model:**
- `backend/app/models/user.py` — `id Uuid PK uuid4`, `username String(50) unique`, `email String(320) unique`, `password_hash String(255) nullable`, `display_name 100`, `bio Text`, `avatar_url/cover_url 512`, `is_active Boolean default true server_default true`, `created_at/updated_at DateTime(timezone=True) server_default func.now()`; убраны дублирующие `Index` (unique уже создаёт constraint)
- `backend/app/models/__init__.py` — импорт User для Alembic

**Schemas:**
- `backend/app/schemas/user.py` — `UserBase` (username 3-50 pattern `^[a-zA-Z0-9_]+$`, EmailStr, display_name 100, bio 500), `UserCreate(password 8-128)`, `UserRead` (from_attributes, id, is_active, timestamps)
- `backend/app/schemas/__init__.py`

**Alembic:**
- `backend/alembic.ini` (script_location alembic)
- `backend/alembic/env.py` — sys.path, `app.models` import, `Base.metadata`, `postgresql+asyncpg`→`psycopg` convert, `target_metadata`, `compare_type/server_default`, online с fallback warning без literal_binds error
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/001_create_users.py` — `revision 001_create_users`, `create_table users` (все колонки, PK, UniqueConstraint email/username), `downgrade DROP TABLE` — `--sql` verified (PostgresqlImpl)

**Docker:**
- `docker-compose.yml` — `postgres:16-alpine`, `container_name bailanysta-postgres`, `POSTGRES_DB/USER/PASSWORD/PORT` via `${POSTGRES_*: -default}`, volume `postgres_data`, healthcheck `pg_isready`, ports `${POSTGRES_PORT:-5432}:5432`
- `.env.example` обновлён: `DATABASE_URL=postgresql+psycopg://...`, `POSTGRES_DB/USER/PASSWORD/PORT` vars
- Docker не установлен на хосте (`docker --version` → not found) — зафиксировано, не блокер для кода

**Health:**
- `backend/app/api/v1/health.py` — сохранён `GET /health` + добавлен `GET /health/db` (check_db_connection, без stack trace, `{"connected"}` / `{"unreachable"}`)

**Tests:**
- `backend/app/tests/conftest.py` — file SQLite `.test_bailanysta.db` (StaticPool, check_same_thread False), `Base.metadata.create_all`, session transaction fixture; docstring объясняет SQLite только для unit-тестов
- `backend/app/tests/test_database.py` — 8 проверок: `test_db_session_creation` (session + SELECT 1), `test_create_and_read_user`, `test_unique_username_constraint`, `test_unique_email_constraint`, `test_timestamps`, `test_rollback_on_error`, `test_is_active_default`, `test_password_hash_nullable` (все PASS, 0.07s)

### Files Changed

```
[mod] backend/requirements.txt (+ psycopg[binary]==3.2.3, email-validator==2.2.0)
[mod] backend/app/core/config.py (psycopg URL, database_url_safe)
[new] backend/app/database/base.py
[new] backend/app/database/session.py
[new] backend/app/database/__init__.py
[new] backend/app/database.py
[new] backend/app/models/user.py
[new] backend/app/models/__init__.py
[new] backend/app/schemas/user.py
[new] backend/app/schemas/__init__.py
[new] backend/alembic.ini
[new] backend/alembic/env.py
[new] backend/alembic/script.py.mako
[new] backend/alembic/versions/001_create_users.py
[new] backend/app/tests/conftest.py
[new] backend/app/tests/test_database.py
[mod] backend/app/api/v1/health.py (+ GET /health/db)
[new] docker-compose.yml
[mod] .env.example (psycopg URL, POSTGRES_* vars)
[mod] backend/app/models/user.py (fix duplicate Index)
[mod] backend/alembic/env.py (fallback fix literal_binds)
```

### Database Changes

- Engine: PostgreSQL via `psycopg` (SQLAlchemy 2.x), `pool_pre_ping True`
- Model: `users` (см. выше) — 11 полей, 2 unique constraints, PK UUID
- Migration: `001_create_users` — create_table users, upgrade/downgrade --sql OK (PostgresqlImpl)
- Session: `SessionLocal`, `get_db()` dependency

### API Changes

- Новый `GET /api/v1/health/db` → `{"status":"ok","database":"connected"}` / `{"status":"error","database":"unreachable"}` (без stack trace)
- Существующий `GET /api/v1/health` не тронут — regression PASS
- Остальные endpoints не созданы (User CRUD — STEP3+)

### Frontend Changes

Нет изменений. Regression: `npx tsc --noEmit` PASS, `npm run build` PASS 3.48s (354.82 kB js gzip 113 kB, 15.29 kB css) — STEP1 не сломан.

### Security Changes

- Никаких plaintext passwords (password_hash nullable, не хранится plain)
- Никаких hardcoded DB passwords (via .env, DATABASE_URL from settings, .env gitignored)
- Никаких credentials в логах (`database_url_safe` masked, health/db без leak)
- `alembic/env.py` не логирует URL с паролем
- Backend-only DB access (get_db dependency), no frontend DB
- Health/db не отдаёт stack trace

### Tests

- `pytest app/tests/test_database.py -v` → **8 passed in 0.07s** (session, create/read, unique username/email, timestamps, rollback, is_active, password_hash)
- `pytest app/tests/test_health.py -v` → **6 passed in 0.36s**
- `pytest -v` (all) → **14 passed, 3 warnings** (SAWarning transaction deassociated — не критично)
- `python -c "from app.database.base import Base; from app.models import User"` → ok, tables ['users']
- `python -c "from app.main import app"` → import ok

### Build

- Frontend: `tsc --noEmit` ✅, `npm run build` 3.48s ✅
- Backend: `import app.main` ✅, `alembic upgrade head --sql` ✅ (CREATE TABLE users ...), `alembic downgrade 001_create_users:base --sql` ✅ (DROP TABLE)
- Online `alembic upgrade head` без PG → OperationalError (ожидаемо, нужен Docker), `alembic current/check` без PG → warning skip (fixed env fallback)

### Problems

- Duplicate Index `ix_users_username already exists` в SQLite при `Base.metadata.create_all` — из-за `unique=True + index=True` + explicit `Index` (duplicate) — fixed удалением `__table_args__` и `index=True`
- `alembic revision --autogenerate` требует живого PG — обошли ручным `001_create_users.py` + `--sql` verify
- `alembic env.py` fallback с `literal_binds=True` без `as_sql` → `Can't use literal_binds without as_sql` — fixed fallback to `return` without configure
- `docker` not found на хосте — cannot run `docker compose up` — зафиксировано как known issue

### Fixed

Все выше исправлено до зелёных тестов. Оставлен file-based SQLite для тестов с пояснением.

### Known Issues

- Docker не установлен — `docker-compose up postgres` нельзя проверить локально (yml валиден, healthcheck есть)
- `alembic upgrade head` требует живого PG (OperationalError без него — ожидаемо)
- SQLite fallback маскирует PG-специфику (UUID, now()) — зафиксировано в conftest, PG constraints проверяются через migration SQL инспекция (PostgresqlImpl)
- `alembic check/current` без PG → warning skip (не критично, online нужен PG)

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| psycopg[binary] 3.2.3 | postgresql+psycopg:// | Современный драйвер SQLAlchemy 2.x (§5) |
| Sync engine (не async) | create_engine + sessionmaker | Простота, без async overhead для MVP |
| User Uuid generic | sqlalchemy Uuid | PG UUID + SQLite совместимость |
| Unique via column unique=True | без duplicate Index | Избежать duplicate index error |
| SQLite file для тестов | conftest file DB | Изолированные unit-тесты без Docker, prod остаётся PG |
| Manual migration 001 | ручной create_table | PG недоступен, но --sql верифицирован |
| Separate /health/db | не ломает /health | Spec §13, быстро и без stack trace |
| docker-compose postgres:16-alpine | env via POSTGRES_* | Spec §6, local dev convenience |

### Next Step

**STEP 3 — Authentication**

- Argon2id, JWT access/refresh HttpOnly cookies, `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- Validation, 409 Conflict duplicate, get_current_user
- Tests auth flow + health/db regression
- Обновить PROJECT_STATE.md + DEVELOPMENT_LOG.md

---

<!-- Шаблон для следующего STEP — копировать и заполнять:

## STEP X — Название

### Date
YYYY-MM-DD

### Objective
Цель STEP.

### Implemented
Что реализовано.

### Files Changed
Список файлов.

### Database Changes
...

### API Changes
...

### Frontend Changes
...

### Security Changes
...

### Tests
...

### Build
...

### Problems
...

### Fixed
...

### Known Issues
...

### Architectural Decisions
...

### Next Step
...

-->
