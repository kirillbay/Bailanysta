# Bailanysta — ARCHITECTURE

> Дата: 2026-09-05 | STEP 0 — Project Initialization
> Статус: Draft (утверждается и уточняется в STEP 1)

---

## 1. Vision & Product Principles

**Bailanysta** — социальная платформа для IT-комьюнити (Social platform for IT communities).

Отвечает на вопрос: «Что происходит в жизни и работе IT-комьюнити?»

Приоритеты (см. MASTER_PROMPT §55):
- **P1 (MVP must-have):** auth, profiles, posts, feed, interactions, backend+DB, deployment, responsive, i18n (ru/kk/en)
- **P2:** clubs, stories, messaging, notifications, projects, search, bookmarks
- **P3:** realtime voice, E2EE, рекомендаций — только после стабильного P1

Принцип: качество > количество (MASTER_PROMPT §54).

---

## 2. High-Level Architecture

```
                ┌─────────────────┐
                │    Browser      │
                │  (React SPA)    │
                └───────┬─────────┘
                        │ HTTPS / JSON / WS
                        ▼
                ┌─────────────────┐
                │  Backend API    │
                │   FastAPI       │
                │  /api/v1/*      │
                └───────┬─────────┘
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
  ┌──────────┐   ┌──────────┐   ┌──────────────┐
  │PostgreSQL│   │ Storage  │   │ External APIs│
  │  (RDS)   │   │ S3 / FS  │   │  (server)    │
  └──────────┘   └──────────┘   └──────────────┘
```

**Критическое правило (§61, §33):** Frontend → Backend → DB/Storage/External. Никаких секретов в браузере, никаких прямых вызовов внешних API с клиента.

---

## 3. Frontend Architecture

### 3.1 Stack

| Слой | Выбор | Обоснование |
|------|-------|-------------|
| Framework | React 18 + TypeScript | Ecosystem, типизация |
| Bundler | Vite | Скорость, HMR |
| Styling | Tailwind CSS + shadcn/ui | Консистентность, скорость, premium look |
| Icons | Lucide | Лёгкость |
| Animations | Framer Motion (по необходимости) | Плавность без перегруза |
| Routing | React Router v6+ | Стандарт |
| Server state | TanStack Query | Кэш, инвалидация, optimistic |
| Forms | React Hook Form + Zod | DX + валидация |
| i18n | i18next + react-i18next | Три языка |
| Client state | Zustand или Context (минимум) | Только где нужен |

### 3.2 Структура

```
frontend/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── package.json
├── public/
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/                 # axios/fetch clients, interceptors
    │   ├── client.ts
    │   └── endpoints/
    ├── components/
    │   ├── ui/              # shadcn primitives (Button, Card, Dialog...)
    │   ├── layout/          # Header, Sidebar, BottomNav, Shell
    │   └── shared/          # Avatar, Skeleton, EmptyState, ErrorState
    ├── features/
    │   ├── auth/
    │   ├── feed/
    │   ├── posts/
    │   ├── profile/
    │   ├── clubs/
    │   ├── messages/
    │   ├── stories/
    │   ├── notifications/
    │   └── search/
    ├── pages/               # Route components (lazy)
    │   ├── FeedPage.tsx
    │   ├── ProfilePage.tsx
    │   ├── ClubPage.tsx
    │   └── ...
    ├── hooks/
    ├── lib/                 # utils, cn, date, validators
    ├── stores/              # authStore, themeStore
    ├── locales/
    │   ├── ru.json
    │   ├── kk.json
    │   └── en.json
    ├── types/
    └── styles/
```

### 3.3 Ключевые решения

- **Routing:** `createBrowserRouter`, protected routes через `<RequireAuth>`, lazy loading страниц.
- **API client:** `fetch` или `axios` с baseURL из `VITE_API_URL`, interceptor для 401 → refresh, credentials: 'include'.
- **i18n:** `i18n` инициализируется с `localStorage` + `navigator.language` fallback; все строки — в `locales/*.json`; переключатель в Header/Profile.
- **Theme:** `next-themes` или кастомный `ThemeProvider` (light/dark/system), сохранение в localStorage, CSS variables.
- **State split (§37):** server state (Query) ≠ UI state (local) ≠ auth state (store+cookie) ≠ preferences (localStorage).
- **Optimistic UI:** для likes/bookmarks/follows — optimistic update с rollback при ошибке.
- **Responsive (§28):** Sidebar → BottomNav на <768px, feed max-width 640-680px, container queries где уместно.

---

## 4. Backend Architecture

### 4.1 Stack

| Слой | Выбор |
|------|-------|
| Language | Python 3.12+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| DB | PostgreSQL 15+ |
| Auth hashing | Argon2id (argon2-cffi) |
| Tokens | JWT (PyJWT) — access (15m) + refresh (7d) в HttpOnly cookies |
| File handling | python-multipart, Pillow (validate), uuid filenames |
| Rate limit | slowapi или custom middleware |
| WS (later) | FastAPI WebSocket / Socket.IO |

### 4.2 Структура

```
backend/
├── pyproject.toml / requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, middleware, routers
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── security.py      # hashing, jwt, cookies
│   │   └── deps.py          # get_current_user, etc.
│   ├── database/
│   │   ├── base.py          # Base, engine, session
│   │   └── session.py
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── follow.py
│   │   ├── story.py
│   │   ├── club.py
│   │   ├── message.py
│   │   └── ...
│   ├── schemas/
│   │   ├── user.py
│   │   ├── post.py
│   │   └── ...
│   ├── api/
│   │   └── v1/
│   │       ├── router.py    # aggregate
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── posts.py
│   │       ├── feed.py
│   │       ├── clubs.py
│   │       └── ...
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── post_service.py
│   │   └── ...
│   ├── repositories/        # опционально, тонкий слой над ORM
│   ├── middleware/
│   │   ├── cors.py
│   │   └── rate_limit.py
│   ├── utils/
│   │   ├── pagination.py    # cursor pagination helpers
│   │   └── upload.py        # file validation
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       └── ...
├── .env.example
└── Dockerfile
```

### 4.3 API Design (§34)

Префикс: `/api/v1`

| Группа | Endpoints (пример) |
|--------|--------------------|
| auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `POST /auth/refresh`, `GET /auth/me` |
| users | `GET /users/{username}`, `PATCH /users/me`, `GET /users/me/followers` |
| posts | `POST /posts`, `GET /posts`, `GET /posts/{id}`, `DELETE /posts/{id}`, `GET /feed` |
| comments | `POST /posts/{id}/comments`, `GET /posts/{id}/comments` |
| likes | `POST /posts/{id}/like`, `DELETE /posts/{id}/like` |
| follows | `POST /users/{id}/follow`, `DELETE /users/{id}/follow` |
| bookmarks | `POST /posts/{id}/bookmark`, `GET /bookmarks` |
| stories | `POST /stories`, `GET /stories`, `DELETE /stories/{id}` |
| clubs | `POST /clubs`, `GET /clubs`, `GET /clubs/{id}`, `POST /clubs/{id}/join`, `POST /clubs/{id}/channels` |
| messages | `GET /conversations`, `POST /conversations`, `GET /conversations/{id}/messages`, `POST /conversations/{id}/messages` (WS: `/ws`) |
| notifications | `GET /notifications`, `POST /notifications/{id}/read` |
| search | `GET /search?q=&type=` |
| projects | `POST /users/me/projects`, `GET /users/{username}/projects` |
| upload | `POST /upload/avatar`, `POST /upload/post-media` |

Все ответы — JSON, ошибки — `{"detail": "..."}` с корректными HTTP статусами (§41).

---

## 5. Database Design

### 5.1 Выбор

- **Prod:** PostgreSQL (Neon / Supabase / Railway)
- **Dev:** PostgreSQL в Docker; SQLite как временный fallback только для unit-тестов, если нужен быстрый прогон (миграции пишутся под Postgres).

### 5.2 Сущности (§10) — эволюционно

**STEP 1 — Core:**
- `users` (id, username unique, email unique, hashed_password, display_name, bio, avatar_url, cover_url, location, role, github_url, linkedin_url, website, is_active, created_at)
- `sessions` / refresh_token (если не stateless) — или JWT без хранения, но с возможностью отзыва

**STEP 2 — Social core:**
- `posts` (id, author_id FK, body, created_at, updated_at)
- `post_media` (id, post_id FK, url, type, order)
- `comments` (id, post_id FK, author_id FK, body, created_at)
- `likes` (user_id, post_id, PK composite)
- `follows` (follower_id, following_id, PK composite)
- `hashtags`, `post_hashtags`, `bookmarks`

**STEP 3 — Stories, Projects:**
- `stories` (id, author_id, media_url, media_type, text, expires_at, created_at)
- `story_views` (story_id, viewer_id)
- `projects` (id, user_id, name, description, technologies[], github_url, demo_url, image_url, status)

**STEP 4 — Clubs:**
- `clubs` (id, slug unique, name, description, avatar_url, owner_id, created_at)
- `club_members` (club_id, user_id, role: owner/admin/member, joined_at)
- `club_channels` (id, club_id, name, type, position)
- `club_messages` (id, channel_id, author_id, body, created_at)

**STEP 5 — Messaging & Notifications:**
- `conversations` (id, created_at)
- `conversation_members` (conversation_id, user_id)
- `messages` (id, conversation_id, sender_id, body, created_at, read_at)
- `notifications` (id, user_id, type, payload, is_read, created_at)

### 5.3 Индексы (§39)

- `users.username` (unique + index), `users.email` (unique + index)
- `posts.author_id`, `posts.created_at` (для feed)
- `likes(post_id, user_id)`, `follows(follower_id, following_id)`
- `comments.post_id`, `hashtags.name`, `club_members(club_id, user_id)`
- `messages.conversation_id + created_at`, `notifications.user_id + is_read`

### 5.4 Миграции

- Alembic, одна миграция на каждый STEP/модуль, именование `001_init_users`, `002_posts` и т.д.
- Никогда не править применённые миграции без новой ревизии.

---

## 6. Authentication (§11)

- **Hashing:** Argon2id (`argon2-cffi`), params по умолчанию библиотеки, pepper не требуется на MVP.
- **Tokens:** JWT HS256 (SECRET_KEY из env), `access_token` 15 мин, `refresh_token` 7 дней.
- **Storage:** `HttpOnly + Secure + SameSite=Lax` cookies (`access_token`, `refresh_token`). В dev `Secure=False`.
- **CSRF:** для cookie-based auth — `Double Submit Cookie` или `SameSite=Lax` + проверка `Origin` на мутациях; альтернатива — `X-CSRF-Token` header.
- **Flow:** `POST /auth/login` → set cookies → `GET /auth/me` → frontend `authStore`; `POST /auth/refresh` по 401; `POST /auth/logout` → clear cookies.
- **Validation:** password min 8 chars, username `^[a-zA-Z0-9_]{3,20}$`, email — RFC 5322 via Pydantic `EmailStr`.

---

## 7. File Uploads (§32)

- **Allowed:** `image/jpeg, image/png, image/webp, image/gif` (MVP), видео — позже
- **Limits:** avatar 2 MB, post image 5 MB, story 10 MB
- **Checks:** MIME + extension + Pillow verify + size
- **Naming:** `uuid4() + ext`, никогда user filename
- **Storage:** `backend/uploads/` в dev (gitignored), S3-совместимое (R2/S3) в prod за абстракцией `StorageService`
- **Serving:** через `/api/v1/uploads/...` (с проверкой) или signed URL в prod

---

## 8. Realtime (этапы)

- **MVP:** polling для messages/notifications (каждые 10-15с) — просто и надёжно.
- **STEP 5+:** WebSocket (`/ws`) для `messages`, `club_messages`, `notifications`; fallback на polling.
- **Voice:** заложить `club_channels.type = 'voice'` в схеме, но без реализации до P1 стабильности.

---

## 9. i18n (§5)

- Файлы: `frontend/src/locales/ru.json`, `kk.json`, `en.json` — плоские ключи `nav.feed`, `post.like`.
- Детекция: `localStorage('lang')` → `navigator.language` → `ru` fallback.
- Переключатель: в header / settings, событие `i18n.changeLanguage` + сохранение.
- Backend: сообщения об ошибках на английском (для логов), пользовательские — по `Accept-Language` позже.

---

## 10. Performance (§38)

- Cursor pagination для feed (`?cursor=<id>&limit=20`)
- TanStack Query `staleTime` + `cacheTime` для feed/profile
- Lazy loading изображений (`loading="lazy"` + blur placeholder)
- DB: индексы, `selectinload`/`joinedload` без N+1, `limit` на все списки
- Frontend: code splitting (React.lazy), memo для PostCard

---

## 11. Deployment (§43)

| Компонент | Prod (план) | Альтернатива |
|-----------|-------------|---------------|
| Frontend | Vercel | Netlify |
| Backend | Render / Railway | Fly.io |
| DB | Neon (Postgres) | Supabase / Railway PG |
| Storage | Cloudflare R2 / S3 | Local (dev) |

- Env через hosting dashboard, никогда в Git.
- CORS: `CORS_ORIGINS` из env, `allow_credentials=True`, конкретные origins в prod.
- Health check: `GET /health` → `{"status":"ok"}`.

---

## 12. Development Workflow (§50-§52)

- Каждый STEP: изучить `PROJECT_STATE.md` → реализовать → тесты → lint → build → обновить `PROJECT_STATE.md`.
- Не ломать существующее (§51), не создавать fake функциональность (§52).
- Seed data — отдельный скрипт `backend/scripts/seed.py`, не в frontend.

---

## 13. Архитектурные решения (trade-offs)

| Решение | Trade-off |
|---------|-----------|
| Cookie JWT vs localStorage | Безопаснее (XSS), но нужен CSRF; выбрано cookie |
| Cursor vs offset pagination | Cursor сложнее, но без дублей/пропусков при новых постах |
| Postgres-only миграции | Чуть сложнее dev, но честная совместимость с prod |
| Polling → WebSocket | Polling проще для MVP, WS позже без ломания API |
| S3 абстракция | Overhead, но готовность к prod без рефактора |

---

## 14. STEP 3 Implementation (2026-09-05)

**Auth реализован:**
- Backend: `app/core/security.py` (Argon2id hash/verify, JWT HS256 sub/exp/iat/type, set/clear HttpOnly cookie `access_token` Lax, Secure=prod, max_age 15m), `app/core/config.py` (SECRET_KEY, algorithm, expire), `app/core/deps.py:get_current_user` (cookie→decode→exp→type→DB→is_active→401), `app/api/v1/auth.py` (register 201 + set cookie 409→username/email, login 200 uniform 401 + is_active, me 200, logout 204 clear), `app/schemas/auth.py`, `app/schemas/user.py:UserRead` (no password_hash)
- Frontend: `api/client.ts` (+post), `api/auth.ts` (me/register/login/logout), `stores/auth.tsx` (useQuery me, AuthProvider, useAuth, logout), `components/RequireAuth.tsx`, `pages/LoginPage.tsx` + `RegisterPage.tsx` (RHF+Zod), `App.tsx` (/login,/register public, AppShell под RequireAuth), `main.tsx` AuthProvider, `components/layout/AppShell.tsx` (user badge + logout)
- Security: HttpOnly Lax Secure prod, CORS credentials, no JWT in localStorage/URL, uniform Invalid credentials, no stack trace, no password leak
- Tests: 25 auth tests (см. DEVELOPMENT_LOG), total 39 passed
- Следующий: **STEP 4 — Profiles**

## 15. STEP 10 Implementation (2026-09-05)

**Channels/Messaging реализован:**
- Models: `ClubChannel` (club_id FK CASCADE, name/slug/description/position, Unique club+slug, index club+position), `ClubMessage` (channel_id FK CASCADE, author_id FK CASCADE, content 1-10000, is_edited, created/updated, index channel+created, author joined)
- Frontend: `api/clubChannels.ts` (9 funcs), `pages/ClubPage.tsx` ChannelsSection (list Link, create owner/admin, edit/delete), `pages/ClubChannelPage.tsx` (grid 240px+1fr, channels sidebar, messages, composer Enter/Shift+Enter, 50 le100, is_edited)
- Relationship: `Club 1—* ClubChannel 1—* ClubMessage N—1 User`, CASCADE delete channel → messages, no realtime (HTTP poll, STEP11 will add WebSocket)
- Следующий: **STEP 11 — Notifications & Realtime (WebSocket)**
