# Bailanysta

> IT Community — социальная платформа для разработчиков и IT-сообщества.

Bailanysta — это современная социальная сеть, где IT-специалисты делятся мыслями, проектами и находят единомышленников. Платформа объединяет привычные паттерны ленты, подписок, клубов и проектов в одном минималистичном продукте для разработчиков, дизайнеров, аналитиков и всех, кто интересуется технологиями.

---

## О проекте

Bailanysta отвечает на вопрос «Что происходит в жизни и работе IT-комьюнити?». Пользователь может опубликовать пост с кодом или GitHub-ссылкой, вступить в тематический клуб (Python, Frontend, AI), обсудить проблему в канале, показать свой проект и получить обратную связь — всё в одном месте, без перегрузки корпоративными функциями. Продукт спроектирован как цельная premium соцсеть, а не как набор разрозненных клонов.

## Возможности

**Пользователи**
- Регистрация и авторизация (Argon2id, JWT HttpOnly)
- Профиль: avatar/cover, bio, display name
- Проекты: showcase с GitHub/demo ссылками

**Социальная часть**
- Посты: создание, редактирование, удаление, изображения (4), hashtags, mentions
- Лента: хронологическая, пагинация, selectinload
- Лайки, комментарии, repost, bookmarks — optimistic UI
- Подписки: follow/unfollow, followers/following, уведомления

**Контент**
- Изображения, ссылки, hashtags, mentions, stories (24ч)

**Clubs**
- Создание клуба, роли owner/admin/moderator/member, участники
- Каналы: создание/удаление (owner/admin), сообщения, редактирование/удаление своих, realtime WebSocket

**Search**
- Пользователи, посты, клубы, проекты, хэштеги (ILIKE, escaped)

**Projects**
- Name, description, technologies (20×50), GitHub/demo URL (валидация), image, статус (idea/in_progress/completed/archived)

**UI**
- RU / KK / EN (i18next, 120+ ключей), Light / Dark / System (no-flash), responsive 360-1440, skeleton/loading/error/empty, mobile BottomNav, a11y (aria, keyboard, focus)

---

## Соответствие заданию

**Level 1 — Профиль и посты**
- Профиль пользователя: avatar, cover, bio, display name, followers/following
- Создание постов: текст + 4 изображения + hashtags, автор, компонентная структура (PostCard, PostComposer, FeedPage)

**Level 2 — Backend и routing**
- Собственный backend: FastAPI + SQLAlchemy 2.x + Pydantic + Alembic
- Интеграция frontend ↔ backend: `fetch` `credentials: include`, TanStack Query, `VITE_API_URL`
- Routing: `React Router` `/`, `/search`, `/clubs/:slug`, `/projects/:projectId`, `/profile/:username`, `/settings` + lazy + `Navigate /explore → /search`

**Level 3 — Запуск и deployment**
- **Quick Start (для проверки):** SQLite + `install.bat` → `http://localhost:5173` (см. ниже)
- **Production:** Docker Compose prod (`docker-compose.prod.yml` + `backend/Dockerfile` + `frontend/Dockerfile` + `nginx.conf` + `nginx.prod.example.conf` + healthchecks + volumes)
- `alembic upgrade head` — миграции, `GET /health` — health

**Bonus**
- Темы Light/Dark/System, лайки, комментарии, редактирование постов, подписки, уведомления (follow/like/comment), loaders/skeletons, поиск (5 типов), клубы/каналы, stories, проекты — всё реализовано и протестировано (284 tests).

*AI integration не реализована (сознательное решение, см. MASTER_PROMPT §59).*

---

## Технологический стек

**Frontend**
React 18, TypeScript 5, Vite 6, Tailwind CSS 3, shadcn/ui, Lucide, React Router 6, TanStack Query 5, React Hook Form + Zod, i18next 24

**Backend**
Python 3.12, FastAPI 0.115, SQLAlchemy 2.0, Pydantic 2, Alembic 1.14, PostgreSQL 16 (prod) / SQLite (local), psycopg 3.2, Argon2id, PyJWT 2.10, Pillow 11

**Realtime**
WebSocket (`/api/v1/ws`, `manager` in-memory, `Upgrade: websocket`)

**Security**
Argon2id, HttpOnly Secure Lax, CSRF Origin check, CORS allowlist, CSP/HSTS/Permissions-Policy, rate limiting (in-memory 20/min), Pydantic validation, upload Pillow verify, authorization/IDOR checks

**Infrastructure**
Docker, Nginx, Docker Compose, `docker-compose.prod.yml` (prod), `docker-compose.yml` (dev postgres)

---

## Почему выбран этот стек

**React/TypeScript** — компонентная архитектура + типизация = масштабируемость и меньше runtime-ошибок. **FastAPI** — Python, скорость разработки, автодокументация OpenAPI, удобная валидация Pydantic. **PostgreSQL** — реляционная модель идеально ложится на связи users/posts/clubs/follows, надёжность и транзакции. **SQLAlchemy + Alembic** — ORM + миграции, структурированная работа с БД, `selectinload` против N+1. **TanStack Query** — серверное состояние, кэш, мутации, инвалидация, optimistic UI. **WebSocket** — realtime для сообщений/уведомлений без polling. **Tailwind/shadcn** — единая UI-система, responsive, быстрая разработка без CSS-хаоса.

---

## Уникальные подходы / Методология

**Документированная разработка**
Каждый STEP фиксировался в `MASTER_PROMPT.md` (68 секций), `PROJECT_STATE.md` (19 секций, persistent memory), `DEVELOPMENT_LOG.md` (история), `ARCHITECTURE.md`, `SECURITY.md`. Это позволило сохранять контекст между перезапусками и работать пошагово 17 STEPS без потери состояния.

**Пошаговая разработка**
`foundation → database → auth → profiles → posts → social → search → stories → clubs → realtime → projects → polish → security → testing → production` — каждый STEP: `PROJECT_STATE` → реализация → `pytest/tsc/build` → `PROJECT_STATE` update.

**Security-first**
Отдельный STEP 14 Hardening (audit 22 критерия, 35 security tests, CSRF, rate limiting, headers) *до* финальной QA — проблемы ловились до релиза.

**Browser QA**
После API-тестов (`TestClient`) проводилась реальная проверка в Chrome (`http://localhost:5173/register` → `Failed to fetch` → найден `dev_bailanysta.db` 0-byte без `app.models` → фикс `Base.metadata.create_all` с импортом). Именно browser QA нашёл расхождение `TestClient` vs `fetch`.

---

## Компромиссы и ограничения

Честно, для демо-версии это допустимо:

- **Realtime single-instance** — `realtime/manager.py` in-memory, без Redis Pub/Sub (требует инфраструктуры, для MVP достаточно)
- **Rate limiter in-memory** — 20/min auth, 30/min search, без Redis (single-instance)
- **Local uploads** — `backend/uploads` volume, без S3/R2 (для демо локально)
- **Offset pagination** — `limit le50`, huge offset → empty (cursor pagination — debt)
- **Bundle ~474kB gz145kB** — lazy 14 routes, но главный chunk близок к 500kB (debt)
- **No private E2EE DMs, voice/video, 2FA, AI moderation** — сознательно отложено (P3)
- **Production Docker smoke test** — `NOT VERIFIED` на Windows без Docker daemon до перезагрузки (честно, не выдумано)

Для демо это не мешает: `Register→Post→Like→Club→Message` полностью работает.

---

## Установка — Quick Start (Windows, без Docker)

> **Важно:** проект сдаётся через **PUBLIC GitHub repository** (`git remote` → GitHub). Скачать ZIP с GitHub (`Code → Download ZIP`) — только как способ локальной проверки, не как способ сдачи.

**Самый простой способ для проверяющего (SQLite, без Docker):**

```powershell
# 1. Требования: Node.js 20+ и Python 3.12+ (проверяет install.bat)
#    Если нет → https://nodejs.org/ (LTS) и https://www.python.org/downloads/

# 2. Скачай репозиторий (ZIP или git clone)
#    Распакуй в C:\Users\lueex\Desktop\Bailanysta

# 3. Запусти (двойной клик)
.\install.bat
# Что делает: проверяет Node/Python → создает .env (генерирует SECRET_KEY) → создает SQLite dev DB
# → pip install -r backend/requirements.txt → npm ci (если нужно) → запускает backend (8000) + frontend (5173)
# → открывает http://localhost:5173 в браузере
```

**Ручной Quick Start (если хочешь контролировать):**

```powershell
# Backend — SQLite
cd backend
$env:DATABASE_URL="sqlite:///./dev_bailanysta.db"
$env:SECRET_KEY="dev-secret-key-not-for-production-32chars-1234567890ab"
python -c "from app.database.base import Base; import app.models; from sqlalchemy import create_engine; e=create_engine('sqlite:///./dev_bailanysta.db'); Base.metadata.create_all(bind=e); print('DB ready')"
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs

# Frontend (новый терминал)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Production / Docker (продвинутый):**

```powershell
.\install.bat  # теперь спрашивает: Quick (SQLite) или Production (Docker)?
# или вручную для Docker:
cp .env.example .env
# заполни SECRET_KEY (openssl rand -hex 32), DATABASE_URL, CORS_ORIGINS=https://..., VITE_API_URL=https://...
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
# Frontend: http://localhost  Backend: http://localhost:8000/health
```

---

## Demo Mode (для комиссии)

На `http://localhost:5173/login` и `/register` есть карта **«Попробовать без регистрации»** → кнопка **«Войти в демо»**:

- `POST /api/v1/auth/demo` → создаёт/берёт `demo / demo@bailanysta.demo / Demo123!` (обычный `HttpOnly` cookie, обычная сессия, rate limited 10/min)
- Демо уже содержит: 3 поста (AI, Rust, Python), комментарии/лайки от `alice_demo`/`bob_demo`, подписки, story, клуб `demo-club` с каналом `general` + 3 сообщения, 2 проекта (`Bailanysta Demo`, `AI Helper`)
- Есть полный вход/регистрация — демо просто ускоряет просмотр

**Логин вручную для теста:**
```text
username: browser_test_qa
email: browser_test_qa@example.com
password: Secret123!
```

---

## Проверка перед публикацией

```powershell
# Секреты: .env не в Git, .env.example без реальных значений
git status --ignored  # должен показать только __pycache__, uploads/, dist/, node_modules/
git ls-files | findstr .env  # должен быть пустым

# Тесты и сборка
cd backend; pytest -q          # 284 passed
cd frontend; npx tsc --noEmit  # PASS
npm run build                  # 474kB

# Миграции
cd backend; python -m alembic upgrade head --sql  # 9/9
```

`.gitignore` уже исключает: `node_modules`, `__pycache__`, `.env`, `*.db`, `uploads/`, `dist/`, `*.log`, `.venv`, `frontend/public` **кроме** `bailanysta-demo-avatar.jpg` (бренд, `!backend/uploads/avatars/bailanysta-demo-avatar.jpg`).

---

## Структура репозитория

```
Bailanysta/
├── backend/               # FastAPI (app/core, database, models, schemas, api/v1, services)
├── frontend/              # Vite React (src/api, components, pages, locales, public/bailanysta-demo-avatar.jpg)
├── install.bat/.ps1       # One-click Windows (SQLite demo, no Docker required)
├── update.bat/.ps1        # Сохраняет .env, build, up -d
├── uninstall.bat/.ps1     # Down без -v (сохраняет данные), -RemoveVolumes требует YES
├── docker-compose.yml     # Dev: postgres only
├── docker-compose.prod.yml# Prod: postgres+backend+frontend volumes + healthchecks
├── nginx.prod.example.conf# HTTP→HTTPS + WSS Upgrade
├── MASTER_PROMPT.md       # 68 секций — источник истины
├── PROJECT_STATE.md       # 19 секций — persistent memory
├── DEVELOPMENT_LOG.md     # История STEPS 0–17
├── ARCHITECTURE.md        # Архитектура
├── SECURITY.md            # Чек-лист
├── DEPLOYMENT.md          # 21 секция + Easy Installation
├── .env.example           # Без секретов
└── README.md              # Ты здесь
```

`install.ps1` лежит в корне — это нормально для Windows double-click, перенос в `installer/` ломает `PSScriptRoot` и README.

---

## Production

- Frontend: `frontend/Dockerfile` `node:20` → `nginx` SPA `try_files`
- Backend: `backend/Dockerfile` `python:3.12-slim` `alembic upgrade head && uvicorn --workers 2`
- DB: `postgres:16-alpine` `postgres_data` persistent, `pg_isready`
- Health: `GET /health` (liveness), `GET /api/v1/health/db` (readiness)
- WSS: `https://` → `wss://` via `getWsUrl()` + nginx `Upgrade`
- Backup: `pg_dump | gzip` + `tar -cz uploads`

См. `DEPLOYMENT.md`.

---

## Известные ограничения

См. раздел «Компромиссы» выше — всё честно задокументировано, не баги, а scope.

---

## Документация

- `MASTER_PROMPT.md` — 68 секций
- `PROJECT_STATE.md` — текущий STEP
- `ARCHITECTURE.md` — решения
- `SECURITY.md` — 18 секций
- `DEPLOYMENT.md` — 21 секция + Easy Install
- `DEVELOPMENT_LOG.md` — STEPS 0–17 + FIXES

---

<p align="center">Built with care for the IT community. Байланыста болайық — stay in touch.</p>
