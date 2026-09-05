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

## STEP 3 — Authentication

### Date

2026-09-05

### Objective

Реализовать production-ready authentication: Argon2id + JWT HttpOnly + register/login/me/logout, защищённые endpoints, frontend auth flow, cookie/CORS/CSRF, comprehensive tests без изменения foundation.

### Implemented

**Backend:**
- `backend/requirements.txt` + `argon2-cffi==23.1.0` + `PyJWT==2.10.1`
- `backend/app/core/config.py` + `algorithm HS256`, `access_token_expire_minutes 15`, `refresh 7`, `secret_key` (placeholder), `SECRET_KEY` already in .env.example
- `backend/app/core/security.py` — `hash_password()` (`PasswordHasher()` default Argon2id t=3 m=65536 p=4), `verify_password()` (VerifyMismatchError), `create_access_token(uuid, minutes)` (sub UUID, exp, iat, type=access, `jwt.encode` HS256), `decode_token` (explicit `algorithms=[HS256]`), `COOKIE_NAME=access_token`, `set_auth_cookie` (httponly True, secure=is_production, samesite Lax, path /, max_age 900), `clear_auth_cookie` (delete_cookie)
- `backend/app/core/deps.py:get_current_user` — cookie → decode → Expired/Invalid → sub UUID parse → DB query → is_active → type check → 401 uniform
- `backend/app/schemas/auth.py` — `RegisterRequest` (username 3-50 regex `^[a-zA-Z0-9_]+$`, EmailStr, password 8-128, display_name 100), `LoginRequest` (identifier, password)
- `backend/app/api/v1/auth.py` — `POST /auth/register` 201 (normalize username strip, email lower, check 409 username/email, IntegrityError race 409, hash_password, User create, token set_auth_cookie, return UserRead no password), `POST /auth/login` 200 (identifier email? lower else username, uniform 401 Invalid credentials, is_active check, set cookie), `GET /auth/me` 200 via get_current_user, `POST /auth/logout` 204 clear cookie (fixed response.status_code)
- `backend/app/api/v1/router.py` — include auth_router
- `ARCHITECTURE.md §14` + `SECURITY.md §2/13/14` updated

**Frontend:**
- `frontend/src/api/client.ts` + `post<T>` method
- `frontend/src/api/auth.ts` — `UserRead`, `authApi.me/register/login/logout` (POST with credentials include)
- `frontend/src/stores/auth.tsx` — `AuthProvider` (useQuery me retry false stale 5m), `useAuth`, `logout` (post + invalidate), `useCurrentUser`
- `frontend/src/components/RequireAuth.tsx` — loading spinner → Navigate /login
- `frontend/src/pages/LoginPage.tsx` — RHF+Zod (identifier, password), serverError, api.login → invalidate me → navigate /
- `frontend/src/pages/RegisterPage.tsx` — RHF+Zod (username regex, email, password 8-128, display_name), serverError
- `frontend/src/App.tsx` — `/login`, `/register` public, AppShell под `<RequireAuth>` protected; errorElement NotFound
- `frontend/src/main.tsx` — `AuthProvider` inside ThemeProvider
- `frontend/src/components/layout/AppShell.tsx` — Sidebar shows `@username` + email + logout button when authenticated
- `frontend/package.json` + `@hookform/resolvers@3.9.0`

### Files Changed

```
[mod] backend/requirements.txt (+ argon2-cffi==23.1.0, PyJWT==2.10.1)
[mod] backend/app/core/config.py (+ algorithm, expire)
[new] backend/app/core/security.py
[new] backend/app/core/deps.py
[new] backend/app/schemas/auth.py
[mod] backend/app/api/v1/auth.py (new)
[mod] backend/app/api/v1/router.py (+ auth_router)
[new] backend/app/tests/test_auth.py (25 tests)
[mod] frontend/src/api/client.ts (+ post)
[new] frontend/src/api/auth.ts
[new] frontend/src/stores/auth.tsx
[new] frontend/src/components/RequireAuth.tsx
[new] frontend/src/pages/LoginPage.tsx
[new] frontend/src/pages/RegisterPage.tsx
[mod] frontend/src/App.tsx (+ /login /register RequireAuth)
[mod] frontend/src/main.tsx (+ AuthProvider)
[mod] frontend/src/components/layout/AppShell.tsx (+ auth badge)
[mod] frontend/package.json (+ @hookform/resolvers)
[mod] ARCHITECTURE.md (§14 STEP3 impl)
[mod] SECURITY.md (§2 status, §13 CSRF, §14 rate limit)
```

### Database Changes

No new migration (users model unchanged, password_hash nullable already). Tests use in-memory StaticPool SQLite for auth (isolated per module), not altering production Postgres.

### API Changes

- `POST /api/v1/auth/register` → 201 UserRead + Set-Cookie access_token (HttpOnly Lax), 409 duplicate username/email, 422 invalid, no password leak
- `POST /api/v1/auth/login` → 200 UserRead + cookie, 401 uniform (wrong/unknown/inactive) with email case-insensitive, username path
- `GET /api/v1/auth/me` → 200 UserRead (no password_hash), 401 missing/invalid/expired/modified/nonexistent/inactive/type
- `POST /api/v1/auth/logout` → 204 + delete_cookie, subsequent me 401
- Existing `GET /health`, `GET /health/db`, `GET /` unchanged — regression PASS

### Frontend Changes

Full auth flow: Login/Register pages (Zod RHF), AuthProvider, RequireAuth redirect, AppShell user badge, logout. Build 1683 modules 447 kB js gzip 138 kB, TSC PASS.

### Security Changes

- Argon2id hash/verify (no plain, no MD5/SHA)
- JWT HS256 explicit alg, no alg=none, SECRET_KEY from env, `sub` UUID, `exp` 15m, `type` check
- Cookie HttpOnly Secure prod SameSite Lax Path/ Max-Age — no localStorage/URL
- CORS `allow_credentials True` + `allow_origins` list (not `*`)
- CSRF: Lax + CORS + Secure documented in SECURITY.md §13 — no double-submit in STEP3
- Rate limit debt documented (§14) — uniform 401, max lengths, no fake protection
- No password/hash/JWT in response, no stack trace leak

### Tests

- `pytest app/tests/test_auth.py -v` → **25 passed in 2.08s**:
  - register 8 (success 201 + cookie HttpOnly + hash not plain, dup username/email/case variant 409, invalid email 422, invalid password 422, invalid username 422, not returned)
  - login 7 (by email 200, by username 200, case-insensitive email 200, wrong pass 401, unknown 401, inactive 401, cookie attrs HttpOnly SameSite Path/)
  - me 6 (auth 200 no hash, no cookie 401, invalid 401, expired 401, modified 401, nonexistent 401)
  - logout 2 (clears + me 401, without auth 401)
  - security 2 (password never, JWT tampered signature/none rejected)
- `pytest -v` all → **39 passed** (25 auth + 8 db + 6 health) 2.38s
- Frontend `tsc --noEmit` PASS, `npm run build` PASS 3.77s

### Build

- Frontend build 1683 modules, 16.66 kB css, 447.93 kB js — PASS
- Backend import ok, routes `/api/v1/auth/*` verified
- `alembic upgrade head --sql` still OK (no new migration)

### Problems

- Logout `Set-Cookie` not sent: `return Response(204)` lost cookie on injected Response — fixed to `response.status_code=204; return response`
- `test_me_modified_token` first tamper `token[:-1]+'a'` still valid due to base64 padding — fixed to `token + 'x'` tamper
- `@hookform/resolvers` missing — installed

### Fixed

All above fixed before green.

### Known Issues

- Rate limiting not yet (debt → STEP14)
- Double-submit CSRF not yet (Lax sufficient for MVP)
- No refresh token flow yet (config placeholder, future)

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| Argon2id default params | argon2-cffi PasswordHasher | Modern, no custom crypto |
| JWT HS256 explicit | PyJWT, no alg none | Security §11 |
| Cookie Lax | not Strict | UX with external links |
| Identifier email OR username | one field | UX simplicity |
| Uniform 401 | Invalid credentials | No enumeration |
| AuthProvider useQuery | not Zustand | Simpler, server state via Query |
| In-memory SQLite for auth tests | StaticPool | Fast without Docker, isolated |

### Next Step

**STEP 4 — Profiles**

- `GET /users/{username}`, `PATCH /users/me`, avatar/bio/display_name, ownership check, tests, frontend profile page

---

## STEP 4 — Profiles

### Date

2026-09-05

### Objective

Реализовать базовую систему профилей: публичный `GET /users/{username}`, own `GET/PATCH /users/me`, avatar/cover upload с безопасным storage, frontend `/profile` и `/profile/{username}` с редактированием и загрузкой, без fake data.

### Implemented

**Backend:**
- `backend/requirements.txt` + `Pillow==11.1.0` + `python-multipart==0.0.9` (installed)
- `backend/app/core/config.py` + `upload_dir="./uploads"`, `max_avatar/cover 5 MB`
- `backend/app/services/storage.py` — `ALLOWED_MIME jpeg/png/webp`, `MAX_MB 5`, `_validate_size` 413, `_detect_and_validate` (Pillow verify + format→ext, 415 on invalid), `save_image` (UUID hex, safe_subdir alphanumeric, `/uploads/<subdir>/<uuid>.ext`, public_url)
- `backend/app/schemas/user.py` — `UserPublic` (id,username,display_name,bio,avatar/cover,created_at) без email/hash, `UserRead` full, `UserUpdate` (display_name 100, bio 500)
- `backend/app/api/v1/users.py` — `GET /users/me` 200 protected, `PATCH /users/me` 200 (only own via get_current_user, strip, 422), `GET /users/{username}` 200 public 404 no email/hash leak, `POST /users/me/avatar` 200 (auth, empty 400, save_image avatars, static check 200), `POST /users/me/cover` 200 (covers); no IDOR endpoint
- `backend/app/api/v1/router.py` — include users_router
- `backend/app/main.py` — `Path(upload_dir).mkdir` + `mount /uploads StaticFiles` (safe, no code exec)
- `.gitignore` already covers `backend/uploads/` + `uploads/` — no files in Git

**Frontend:**
- `frontend/src/api/client.ts` + `patch<T>`
- `frontend/src/api/users.ts` — `UserPublic`, `UserMe`, `usersApi.me()/public()/update()/uploadAvatar()/uploadCover()` (FormData POST credentials include), `resolveUrl` (API_URL prefix)
- `frontend/src/pages/ProfilePage.tsx` — cover (gradient fallback, coverUrl, preview), Avatar component (initial or img), display_name/username/bio/created_at, own edit toggle (RHF Zod display_name 100 bio 500), upload buttons (accept jpeg/png/webp, preview URL.createObjectURL, uploading state, msg, invalidate queries on success), Card future posts
- `frontend/src/App.tsx` — `/profile` + `/profile/:username` → `ProfilePage`, still protected via RequireAuth

### Files Changed

```
[mod] backend/requirements.txt (+ Pillow, python-multipart)
[mod] backend/app/core/config.py (+ upload_dir, max sizes)
[new] backend/app/services/storage.py
[mod] backend/app/schemas/user.py (+ UserPublic, UserUpdate)
[new] backend/app/api/v1/users.py
[mod] backend/app/api/v1/router.py (+ users_router)
[mod] backend/app/main.py (+ StaticFiles /uploads)
[mod] frontend/src/api/client.ts (+ patch)
[new] frontend/src/api/users.ts
[new] frontend/src/pages/ProfilePage.tsx
[mod] frontend/src/App.tsx (+ /profile/:username)
[new] backend/app/tests/test_profiles.py (18 tests)
```

### Database Changes

No migration (users already has avatar_url, cover_url, display_name, bio). `001_create_users` remains.

### API Changes

- `GET /api/v1/users/me` → 200 UserRead (auth), 401 unauth — reuse auth, not duplicating /auth/me logic (separate endpoint for users domain)
- `PATCH /api/v1/users/me` → 200 updated, 422 bio>500, 401 unauth
- `GET /api/v1/users/{username}` → 200 UserPublic (no email/hash/JWT), 404
- `POST /api/v1/users/me/avatar` → 200 UserRead avatar_url `/uploads/avatars/<uuid>.ext`, 401, 415 unsupported, 413 oversized, safe filename no traversal
- `POST /api/v1/users/me/cover` → 200 cover_url similarly
- `GET /uploads/...` static — served, no code execution

### Frontend Changes

ProfilePage with real data, edit form, upload preview/loading/error, TanStack Query (me + public + mutation invalidate), no fake counts, no reload.

### Security Changes

- No email/hash leak via public profile (UserPublic)
- Ownership only own (get_current_user, no ID param)
- No IDOR PATCH other user (no endpoint)
- Upload: auth required, MIME allowlist jpeg/png/webp, Pillow verify, UUID filename, safe_subdir, no user path, size 5 MB 413, no path traversal (`../../etc/passwd` → safe), generated unique, stored outside code, static mount safe, no exec
- UPLOAD_DIR via env, gitignored, public_url not filesystem path

### Tests

- `pytest app/tests/test_profiles.py -v` → **18 passed in 2.77s**:
  - public 3 (success no email/hash, 404, no jwt), own 2 (auth 200, unauth 401), update 4 (own success persisted, 422, no IDOR 404, unauth 401), uploads 8 (avatar/cover success + static 200, unauth 401, unsupported 415, oversized 413/415, malicious filename safe, unique filename, no traversal, email leak after update), plus 1 public after update email leak
- `pytest -v` all → **57 passed** (25 auth + 8 db + 6 health + 18 profiles) 4.48s
- Frontend `tsc --noEmit` PASS, `npm run build` PASS 3.25s (458.08 kB js gzip 141.60 kB)

### Build

- Frontend 1685 modules, 17.77 kB css
- Backend `python -c "from app.main import app"` routes include /users/* + /uploads verified

### Problems

- `import app.models` shadowed `from app.main import app` → `AttributeError: module 'app' has no attribute 'dependency_overrides'` — fixed by `from app.main import app as fastapi_app`
- Stray `@pytest.fixture_scope if False` left in test file → TypeError — removed

### Fixed

Both fixed before green.

### Known Issues

- Local uploads `./uploads` — MVP, S3 abstraction ready via `services/storage.py` (STEP16)
- No username editing (immutable per ARCHITECTURE)
- No delete avatar/cover endpoint (overwrite via upload)
- Docker absence (known)

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| LocalStorage + Pillow verify | UUID hex + safe_subdir | Security + S3 later without API break |
| UserPublic separate schema | no email/hash | Privacy |
| PATCH /users/me only own | no PATCH /users/{id} | IDOR prevention |
| Static /uploads mount | StaticFiles | Simple serve, no exec |
| Frontend preview via ObjectURL + invalidate | TanStack Query | UX immediate |

### Next Step

**STEP 5 — Posts & Media**

- `posts` model + migration, `POST /posts` (text+hashtags), media storage, tests, frontend composer

---

## STEP 5 — Posts & Media

### Date

2026-09-05

### Objective

Реализовать настоящую систему постов: Post/Media/Hashtag модели, медиа лимиты, CRUD API с пагинацией, hashtags, frontend composer + PostCard + detail + edit/delete, без likes/comments/follows.

### Implemented

**Backend:**
- `backend/app/models/post.py` — `Post` (UUID PK, author_id FK CASCADE index, content Text, created_at index, updated_at, author joined, media selectin, hashtags selectin, ix_posts_author_created), `PostMedia` (UUID PK, post_id FK CASCADE, url 512, mime 50, position Unique post/position, index), `Hashtag` (UUID PK, name 100 unique index lower), `post_hashtags` (PK composite CASCADE)
- `backend/app/models/__init__.py` — export Post, PostMedia, Hashtag
- `backend/alembic/versions/002_create_posts.py` — hashtags, posts, post_media, post_hashtags — `--sql` PostgresqlImpl verified
- `backend/app/services/hashtags.py` — `HASHTAG_RE #\w{1,50}`, MAX 20, MAX_LEN 50, lower, dedup, limit
- `backend/app/schemas/post.py` — `AuthorPublic`, `PostMediaRead`, `PostRead` (author, media, hashtags), `PostCreateInput` 1-10000, `PostUpdateInput` 1-10000
- `backend/app/api/v1/posts.py` — `POST /posts` 201 (Form content 1-10000 + files Optional 0-4, stripped+media check, save_image posts/ with cleanup on fail, Post+PostMedia+hashtags transaction, delete orphan file handling), `GET /posts/{id}` 200 404 public, `GET /posts/by/user/{username}` + `GET /users/{username}/posts` alias 200 pagination limit 20 le50 offset, `PATCH /posts/{id}` 200 owner 403 hashtags recalc, `DELETE /posts/{id}` 204 owner 403 cascade + file unlink
- `backend/app/api/v1/users.py` — added `GET /users/{username}/posts` alias (before generic), uses _post_to_read
- `backend/app/api/v1/router.py` — include posts_router
- `frontend/src/api/posts.ts` — create via FormData POST, get, userPosts, patch, remove, resolveUrl
- Storage reuse: `posts/` subdir separate from avatars/covers

**Frontend:**
- `frontend/src/components/PostComposer.tsx` — avatar, textarea placeholder, counter 10000, picker max 4, previews URL.createObjectURL + remove, POST button disabled, invalidate posts/user-posts
- `frontend/src/components/PostCard.tsx` — author avatar fallback, name/username/timestamp, content split hashtags colored, media grid 1/2, hashtags badges, owner edit (textarea + save/cancel), delete confirm, link to detail, invalidate
- `frontend/src/pages/FeedPage.tsx` — hero + PostComposer + useQuery user-posts + health card (updated to STEP5 badge)
- `frontend/src/pages/PostDetailPage.tsx` — useParams postId, useQuery get, skeleton/404, PostCard
- `frontend/src/App.tsx` — `/posts/:postId` protected

### Files Changed

```
[new] backend/app/models/post.py
[mod] backend/app/models/__init__.py (+ Post, Hashtag)
[new] backend/alembic/versions/002_create_posts.py
[new] backend/app/services/hashtags.py
[new] backend/app/schemas/post.py
[new] backend/app/api/v1/posts.py
[mod] backend/app/api/v1/users.py (+ GET /users/{username}/posts alias)
[mod] backend/app/api/v1/router.py (+ posts_router)
[new] backend/app/tests/test_posts.py (29 tests)
[new] frontend/src/api/posts.ts
[new] frontend/src/components/PostComposer.tsx
[new] frontend/src/components/PostCard.tsx
[new] frontend/src/pages/PostDetailPage.tsx
[mod] frontend/src/pages/FeedPage.tsx (+ composer + user posts feed)
[mod] frontend/src/App.tsx (+ /posts/:postId)
```

### Database Changes

- New tables: `posts`, `post_media`, `hashtags`, `post_hashtags` — FK CASCADE, indexes, unique constraints
- Migration `002_create_posts` — upgrade/downgrade --sql OK

### API Changes

- `POST /api/v1/posts` (multipart content + files) → 201 PostRead + media + hashtags, 401, 422 (empty, oversized, max 4)
- `GET /api/v1/posts/{id}` → 200 PostRead public 404
- `GET /api/v1/users/{username}/posts?limit&offset` + `GET /api/v1/posts/by/user/{username}` → 200 list paginated 50 max, 404 user, 422 limit>50
- `PATCH /api/v1/posts/{id}` → 200 updated + hashtags, 403 not owner, 404, 422
- `DELETE /api/v1/posts/{id}` → 204, 403, 404 + file cleanup best effort

### Frontend Changes

Composer + PostCard + Feed + Detail with real API, no fake counters, edit/delete with confirmation, hashtag highlight, TanStack Query invalidate.

### Security Changes

- Auth required for create/patch/delete, public read
- Ownership via `post.author_id != current_user.id` → 403, no author_id bypass (PostUpdateInput only content)
- Content length 1-10000, empty rejected unless media, max 4 files enforced backend
- MIME via save_image Pillow verify, filename sanitized UUID, subdir posts/, no path traversal
- No HTML rendering (whitespace text, hashtag span), XSS safe (React escape)
- Transaction + file cleanup on DB fail (documented limitation not atomic but safe)

### Tests

- `pytest app/tests/test_posts.py -v` → **29 passed in 4.58s**:
  - posts 5 (auth, unauth 401, empty 422, oversized 422, author public)
  - media 8 (jpeg/png/webp, unsupported 415, oversized 413, invalid content 415, malicious safe, max 4 enforced, dir posts/)
  - read 4 (existing, 404, pagination 2+2, limit 422)
  - ownership 5 (update/delete owner, other cannot update/delete 403, forged author_id ignored)
  - hashtags 4 (extract python/ai duplicate, normalization lower, duplicate, excessive limit 20)
  - delete 2 (media records removed + file cleanup, edit updates hashtags)
- `pytest -v` all → **86 passed** (25 auth + 8 db + 6 health + 18 profiles + 29 posts)
- Frontend `tsc --noEmit` PASS, `npm run build` 1689 modules 464.78 kB js gzip 143.51 kB

### Build

- Frontend 3.52s, 18.34 kB css
- Backend import ok, routes /posts + /users/{username}/posts verified, `alembic upgrade head --sql` both migrations OK

### Problems

- `FeedPage.tsx` imports with backslash `\\` due to Windows path → TS2307 — fixed to `/`
- `posts` PATCH used `payload: dict` — no validation — fixed to `PostUpdateInput` Pydantic
- Users `GET /users/{username}` conflict with `GET /users/{username}/posts` — fixed by ordering + alias
- `List[UploadFile] = File(default=[])` caused issues with no files — fixed to `Optional[List[UploadFile]] = File(None)` + `files or []`

### Fixed

All fixed before green.

### Known Issues

- Feed is user-posts only (no global feed ranking — STEP6)
- No likes/comments (STEP6)
- Hashtag search not yet (tables ready)
- Media editing on patch immutable (documented)
- Physical cleanup best effort (documented)

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| Content 10000 | 1-10000 + empty if media | Spec §5-9 |
| Storage posts/ separate | reuse storage.py | Clean separation |
| Hashtag #\w 1-50 lower dedup max20 | regex + lower | Spec §16, STEP7 ready |
| Multipart Form content+files | one POST | Spec §9 clean API |
| Offset pagination limit 50 | Query ge1 le50 | MVP spec §12 |
| Cascade delete + file unlink | best effort | Spec §14 limitation |

### Next Step

**STEP 6 — Feed & Social Interactions**

- Global feed, likes/comments/reposts/bookmarks, Post interactions, optimistic UI

---

## STEP 6 — Feed & Social Interactions

### Date

2026-09-05

### Objective

Сделать из списка постов настоящую социальную ленту (global feed) и добавить базовые взаимодействия: likes, comments, reposts, bookmarks, optimistic UI, loading/empty/error.

### Implemented

**Backend:**
- `backend/app/models/social.py` — `PostLike` (UUID PK, post/user FK CASCADE, Unique post+user, indexes), `Comment` (UUID PK, post FK CASCADE, author FK CASCADE, content Text, created/updated, author joined, index post+created), `PostRepost` (UUID PK, post/user CASCADE Unique), `Bookmark` (UUID PK, post/user CASCADE Unique, index user+created)
- `backend/app/models/__init__.py` + social exports
- `backend/alembic/versions/003_create_social.py` — post_likes, comments, post_reposts, bookmarks — `--sql` verified
- `backend/app/schemas/post.py` + `likes_count, comments_count, reposts_count, liked_by_me, reposted_by_me, bookmarked_by_me`
- `backend/app/schemas/comment.py` — AuthorPublic, CommentRead, Create 1-2000, Update 1-2000
- `backend/app/api/v1/posts.py` enriched `_enrich_many` bulk counts (func.count group_by + sets liked/reposted/bookmarked), `_get_current_user_optional`, `GET /posts/{id}` public optional auth, `GET /posts/by/user` enriched, `PATCH/DELETE` enriched, `POST/DELETE /posts/{id}/like|repost|bookmark` (auth, 404, idempotent Already liked/detail, 204 unlike), `POST /posts/{id}/bookmark` etc
- `backend/app/api/v1/feed.py` — `GET /feed` auth `created_at DESC` limit50 offset, _enrich bulk
- `backend/app/api/v1/comments.py` — `GET /posts/{id}/comments` public pagination 50, `POST /posts/{id}/comments` auth 201, `PATCH /comments/{id}` owner 403, `DELETE` owner, content 1-2000
- `backend/app/api/v1/bookmarks.py` — `GET /bookmarks` auth user_created desc, enrich, preserves bookmark order
- `backend/app/api/v1/users.py` — `GET /users/{username}/posts` enriched counts (bulk), `router.py` includes feed/comments/bookmarks
- Tests `app/tests/test_social.py` 24 passed (feed 4, likes 5, comments 8, reposts 3, bookmarks 4)

**Frontend:**
- `frontend/src/api/posts.ts` + like/unlike/repost/unrepost/bookmark/unbookmark, `api/feed.ts`, `api/comments.ts`, `api/bookmarks.ts`
- `frontend/src/components/PostCard.tsx` — interaction bar (Heart red fill, MessageCircle, Repeat2 green, Bookmark blue fill, Share2 copy), optimistic toggle with rollback + invalidate feed/bookmarks, edit/delete, CommentSection (list, create, edit/delete own), withComments prop, counts from PostRead
- `frontend/src/pages/FeedPage.tsx` — global feed `feedApi.get` offset, allPosts accumulation, skeleton/empty/error, load more, composer invalidate feed
- `frontend/src/pages/PostDetailPage.tsx` — withComments true, skeleton/404, PostCard
- `frontend/src/pages/BookmarksPage.tsx` — `bookmarksApi.list`, empty state, PostCard
- `frontend/src/App.tsx` — `/bookmarks` protected

### Files Changed

```
[new] backend/app/models/social.py
[mod] backend/app/models/__init__.py (+ social)
[new] backend/alembic/versions/003_create_social.py
[mod] backend/app/schemas/post.py (+ counts)
[new] backend/app/schemas/comment.py
[mod] backend/app/api/v1/posts.py (enriched + like/repost/bookmark)
[new] backend/app/api/v1/feed.py
[new] backend/app/api/v1/comments.py
[new] backend/app/api/v1/bookmarks.py
[mod] backend/app/api/v1/users.py (enriched)
[mod] backend/app/api/v1/router.py (+ feed/comments/bookmarks)
[new] backend/app/tests/test_social.py (24 tests)
[mod] frontend/src/api/posts.ts (+ like/repost/bookmark)
[new] frontend/src/api/feed.ts
[new] frontend/src/api/comments.ts
[new] frontend/src/api/bookmarks.ts
[mod] frontend/src/components/PostCard.tsx (interaction bar + comments + optimistic)
[new] frontend/src/pages/BookmarksPage.tsx
[mod] frontend/src/pages/FeedPage.tsx (global feed)
[mod] frontend/src/pages/PostDetailPage.tsx (withComments)
[mod] frontend/src/App.tsx (+ /bookmarks)
```

### Database Changes

- Migration `003_create_social` — post_likes, comments, post_reposts, bookmarks — `--sql` OK, FK CASCADE, Unique, indexes

### API Changes

- `GET /api/v1/feed?limit&offset` → 200 global feed DESC with counts/liked/bookmarked, 401 unauth
- `POST /api/v1/posts/{id}/like` 201, `DELETE` 204 idempotent, `GET /posts/{id}` now with counts/liked
- `POST /api/v1/posts/{id}/repost` 201, `DELETE` 204, counts
- `POST /api/v1/posts/{id}/bookmark` 201, `DELETE` 204, `GET /api/v1/bookmarks` auth only own
- `GET /api/v1/posts/{id}/comments?limit&offset` public, `POST` auth 201, `PATCH /comments/{id}` owner 403, `DELETE` owner

### Frontend Changes

Feed global + load more, PostCard interactions optimistic with rollback, Bookmarks page, PostDetail comments, Share copy link, TanStack Query feed/post/bookmarks/comments invalidation.

### Security Changes

- All mutations require get_current_user (401), IDOR checks for comment edit/delete (author_id), like/repost/bookmark isolated per user (Unique prevents duplicate), no HTML (text), XSS safe, empty/too long 422, malformed UUID 422, nonexist 404

### Tests

- `pytest app/tests/test_social.py -v` → **24 passed in 4.19s**:
  - feed 4 (auth, pagination 2+2, empty, requires auth)
  - likes 5 (like/unlike counts + flags, duplicate idempotent, unauth 401, nonexist 404, isolation)
  - comments 8 (create/read, update own, delete own, cannot update other 403, empty 422, too long 422, unauth 401, nonexist 404)
  - reposts 3 (repost/unrepost + counts, duplicate, unauth)
  - bookmarks 4 (bookmark/remove + flags + GET /bookmarks, duplicate, isolation, unauth)
- `pytest -v` all → **110 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social)
- Frontend `tsc --noEmit` PASS, `npm run build` 1692 modules 469.60kB js gzip 144.19kB

### Build

- Frontend 3.61s, 16.45kB css
- Backend import ok, routes verified, `alembic upgrade head --sql` all 3 migrations OK

### Problems

- `users.py` imported `_post_to_read` removed after enrichment — fixed to bulk enrich locally
- Initial posts `GET /posts/{id}` not enriched (no counts) — fixed to `_enrich_single` with optional auth
- Feed `allPosts` accumulation with offset re-fetch caused duplication without `offset` state reset — fixed to offset state + setAllPosts
- PostCard optimistic rollback needed explicit wasLiked capture — fixed

### Fixed

All fixed before green.

### Known Issues

- Feed is global chronological, no personalization
- Comments flat only, no pagination load more beyond 20 fixed
- Bookmarks pagination fixed 20
- No markdown

### Architectural Decisions

| Решение | Выбор | Причина |
|---------|-------|---------|
| Bulk counts via group_by | not N+1 | Spec §6 performance |
| Optimistic like/bookmark with rollback | useState optimistic + fetch catch rollback | Spec §2/9 UX safe |
| Unique post+user | idempotent Already liked | Spec §2/4/5 |
| Flat comments 1-2000 | no nested | Spec §3 MVP |
| Migration 003 separate | not rewrite old | Spec §10 |

### Next Step

**STEP 7 — Follow / Search / Hashtags**

- Follow model, search users/posts/hashtags, hashtag search via existing tables

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
