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
