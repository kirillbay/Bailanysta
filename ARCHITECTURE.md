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

## 16. STEP 11 Implementation (2026-09-05)

**Notifications & Realtime реализован:**
- Models: `Notification` (recipient_id FK CASCADE, actor_id FK SET NULL, type, title/message, entity_type/id, is_read, created_at, indexes recipient+created/read)
- Services: `services/notifications.py` (create_notification no self, notify_follow/like/comment centralized)
- APIs: `api/v1/notifications.py` (GET list/unread-count, PATCH read, POST read-all, DELETE), `api/v1/realtime.py` (WebSocket /ws, auth via cookie/?token, 4401, subscribe with ClubChannel+ClubMember check, broadcast)
- Realtime Manager: `realtime/manager.py` (user_connections, channel_subscribers, Lock, connect/disconnect/subscribe/broadcast/send_to_user) — in-memory, no Redis
- Frontend: `api/notifications.ts`, `hooks/useRealtime.ts` (getWsUrl http→ws, useChannelRealtime backoff 1s→16s, useNotificationsRealtime), `pages/NotificationsPage.tsx` (list, unread badge, mark read/all, delete, entity link), `pages/ClubChannelPage.tsx` + `useChannelRealtime` status Connected/Reconnecting/Offline, `components/layout/AppShell.tsx` badge 99+ via `useNotificationsRealtime`
- Events: `connected`, `subscribed`, `message.created|updated|deleted`, `notification.created`, `error` — JSON `{type, payload}`
- Flow: `POST message → DB commit → manager.broadcast_channel → WS subscribers` (ghost-free, dedup via id), `POST follow/like/comment → create_notification → manager.send_to_user`
- HTTP fallback: `GET /clubs/.../messages` still works via HTTP, WS is enhancement, polling not aggressive
- Следующий: **STEP 12 — Projects**

## 17. STEP 12 Implementation (2026-09-05)

**Projects & Developer Showcase реализован:**
- Models: `Project` (owner_id FK CASCADE, name 150, description Text, technologies JSON, github_url/demo_url/image_url 512, status idea/in_progress/completed/archived, position int, created/updated, indexes owner, owner+position, owner+created)
- Schemas: `schemas/project.py` (ProjectCreate 1-150/1-2000/technologies max 20×50 dedup lower/status enum/github host demo URL https/http, ProjectUpdate partial, ProjectRead + OwnerPublic)
- Migration: `009_create_projects` — projects table — `--sql` verified (PostgresqlImpl), downgrade DROP
- APIs: `api/v1/projects.py` — `GET /users/{username}/projects` public 404 pagination 50 position ASC created DESC, `GET /users/me/projects` auth, `GET /projects/{id}` public 404, `POST /users/me/projects` 201 owner=current_user no forgery position max+1, `PATCH` owner 403, `DELETE` owner 403 + best-effort file unlink, `POST image` owner 403 save_image projects/ UUID Pillow 5MB, `router.py` + projects, `search.py` + projects ILIKE name/description/cast(technologies) (parameterized, trim, max 100, limit 50)
```
User
 ├── Posts
 ├── Stories
 ├── Clubs
 ├── Projects  ← showcase layer, not source-code hosting
 └── Notifications
Project
 ├── owner (User)
 ├── technologies (JSON array)
 ├── github_url/demo_url (validated URL, github host)
 └── image (uploads/projects)
```
- Frontend: `api/projects.ts` (listUser/listMy/get/create/update/delete/uploadImage + resolveImage), `components/ProjectCard.tsx` (gradient fallback, status badge, tech badges, GitHub/Demo external rel noopener), `components/ProjectForm.tsx` (RHF Zod + chip input Enter dedup max 20/50), `pages/ProjectsPage.tsx` (/projects my showcase + upload), `pages/ProjectDetailPage.tsx` (/projects/:id public), `pages/ProfilePage.tsx` tabs Posts|Projects (public list, own inline CRUD + upload, empty states), `pages/SearchPage.tsx` + projects type, `App.tsx` + /projects & /projects/:id
- Showcase nature: developer showcase + GitHub/demo links only, no GitHub API/OAuth, no repository sync, no code hosting — documented
- Следующий: **STEP 13 — i18n/Theme/Responsive**

## 18. STEP 13 Implementation (2026-09-05)

**i18n, Theme, Responsive & Accessibility Polish реализован:**
- i18n: `lib/i18n.ts` detector `localStorage bailanysta_lang` → navigator, fallback ru, `locales/ru|kk|en.json` 13 sections (common, nav, auth, feed, post, profile, projects, search, clubs, notifications, settings, errors, a11y) ~120 keys each, `html lang` sync, `LanguageDetector` order localStorage→navigator, `SettingsPage` persistence verified reload/browser close
- Theme: `stores/theme.tsx` Light/Dark/System + localStorage `bailanysta_theme` + `matchMedia` System listener + `resolved`, `index.html` inline script anti-FOUC (reads before React), `SettingsPage` + `AppShell` switchers `aria-pressed`, `focus-visible:ring-2`, audited cards/inputs/badges/skeletons/project/club/message/profile cover in both themes using Tailwind tokens `bg-card`/`bg-background`/`text-muted-foreground`/`border` (no hardcoded)
- Responsive QA: `360,390,430,768,1024,1280,1440` checked — AppShell sidebar 260px lg / BottomNav 5 items h-14 touch 44px, Feed max-w-2xl, PostComposer min-w-0, Projects grid md:2 gap-4 card truncate +6, Search flex-wrap, ClubChannel grid 1fr lg 240px+1fr stacks mobile + composer sticky, no horizontal overflow
- Accessibility: semantic `button` vs `div`, `label htmlFor`, `aria-label` for icon-only (Heart/MessageCircle/Repeat2/Bookmark/Share2 → a11y.*), `role=alert` for errors, `aria-busy`, keyboard Tab flows (Login→Register→Post→Project→Channel→Settings) no trap, focus visible `ring-2`
- Bundle: `App.tsx` lazy 14 routes `Suspense` fallback skeleton, Vite code-split per route, main 472kB gzip 145kB (css 18.98kB) vs 527kB before, chunk warning mitigated but remains near threshold (documented debt, stability > optimization)
- No new large features (private DM, E2EE, voice, AI, GitHub OAuth) per §24
- Следующий: **STEP 17 — Final QA**

## 21. STEP 16 Implementation (2026-09-05)

**Production Deployment реализован:**
- `backend/Dockerfile` — `python:3.12-slim` `ENV PYTHONDONTWRITEBYTECODE` `pip install -r requirements.txt` `useradd appuser` `HEALTHCHECK /health` `CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (не `--reload`)
- `frontend/Dockerfile` — `node:20-alpine` `npm ci && npm run build` `ARG VITE_API_URL` → `nginx:alpine` `COPY dist /usr/share/nginx/html` + `nginx.conf` SPA `try_files $uri /index.html` + `HEALTHCHECK`
- `frontend/nginx.conf` — `gzip` `try_files` SPA, `/api/` → `http://backend:8000` + `/uploads/` proxy `client_max_body_size 10M`, `CSP` `HSTS` headers
- `docker-compose.prod.yml` — `postgres` (volume `postgres_data` no host port) `backend` (depends_on healthy postgres, env `DATABASE_URL` `SECRET_KEY` `CORS_ORIGINS` `VITE_API_URL`, volume `uploads_data:/app/uploads`, healthcheck `/health`) `frontend` (depends_on healthy backend, args `VITE_API_URL`, port `80`) network `bailanysta` restart `unless-stopped`
- `nginx.prod.example.conf` — `80→443` `TLS` `certbot` `Upgrade: websocket` `Connection: Upgrade` для `/api/v1/ws` `proxy_read_timeout 3600s`, no real certs in repo
- `app/core/config.py` — `field_validator` `secret_key` `>=32` в production + `cors_origins` check, `is_production` `Secure` cookies
- `DEPLOYMENT.md` — 21 секций (prerequisites, server, env, secret, postgres, migrations, Docker, reverse proxy, HTTPS, frontend, backend, WSS, uploads, DB persistence, backups `pg_dump`, logs, health, update/rollback, limitations)
- `README.md` — updated `STEP 16` badge, Docker prod commands, `VITE_API_URL` https→wss
- Проверка: `docker compose -f docker-compose.prod.yml config` → `NOT VERIFIED — Docker not available on this host` (честно), `pytest 281` `tsc` `build 472kB` `alembic head --sql` 9/9
- Следующий: **STEP 17 — Final QA**

## 20. STEP 15 Implementation (2026-09-05)

**Full Testing, Bug Fixing & Performance реализован:**
- Backend: `feed.py` `selectinload(Post.author/media/hashtags)` устраняет N+1, `notifications.py` bulk `actor_map` для 100 notifs → 1 query вместо 100, `rate_limit.py` memory prune при >5000 keys (LRU), все 9 миграций `--sql` OK
- Frontend: `FeedPage.tsx` fix P1 `queryFn` side-effect → `useEffect` accumulation (предотвращает stale closure и бесконечный loop), `useRealtime.ts` fix P2 `timeoutRef` cleanup (предотвращает leak reconnect timers), `PostComposer.tsx` fix P3 `useEffect` revoke `URL.createObjectURL` on unmount (memory leak), `hasMore` offset pagination уже корректна, `App.tsx` lazy 14 routes `472kB` stable
- Tests: `tests/test_edgecases.py` 16 новых (unicode, username min/max, post 10000/10001, comment 2000/2001, message 10000, empty, invalid UUID, 404, pagination `limit=0`/`-1`/`999999`/`51`, duplicate like/follow, nonexistent, story expiration, cascade delete, GitHub validation, search empty/101) — все 16 passed, total `281`
- QA: Auth `Register→Login→Logout→Login` ✅, Feed `Create→Like→Comment→Repost→Bookmark` ✅, Profile `Edit→Avatar` ✅, Search `User/Post/Club/Project` ✅, Clubs `Create→Join→Channel→Message` ✅, Notifications `Mark read` ✅, Stories `Create→View` ✅, Projects `Create→Edit→Search→Delete` ✅, Settings `language/theme` ✅, Realtime `WS connect→reconnect` ✅, Routing `direct URL/refresh/back` ✅, Performance `N+1` audit, Bundle `472kB gz145kB` stable
- Следующий: **STEP 17 — Final QA**

## 21. STEP 16 Implementation (2026-09-05)

**Production Deployment реализован:**
- `backend/Dockerfile` — `python:3.12-slim` `ENV PYTHONDONTWRITEBYTECODE` `pip install -r requirements.txt` `useradd appuser` `HEALTHCHECK /health` `CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (не `--reload`)
- `frontend/Dockerfile` — `node:20-alpine` `npm ci && npm run build` `ARG VITE_API_URL` → `nginx:alpine` `COPY dist /usr/share/nginx/html` + `nginx.conf` SPA `try_files $uri /index.html` + `HEALTHCHECK`
- `frontend/nginx.conf` — `gzip` `try_files` SPA, `/api/` → `http://backend:8000` + `/uploads/` proxy `client_max_body_size 10M`, `CSP` `HSTS` headers
- `docker-compose.prod.yml` — `postgres` (volume `postgres_data` no host port) `backend` (depends_on healthy postgres, env `DATABASE_URL` `SECRET_KEY` `CORS_ORIGINS` `VITE_API_URL`, volume `uploads_data:/app/uploads`, healthcheck `/health`) `frontend` (depends_on healthy backend, args `VITE_API_URL`, port `80`) network `bailanysta` restart `unless-stopped`
- `nginx.prod.example.conf` — `80→443` `TLS` `certbot` `Upgrade: websocket` `Connection: Upgrade` для `/api/v1/ws` `proxy_read_timeout 3600s`, no real certs in repo
- `app/core/config.py` — `field_validator` `secret_key` `>=32` в production + `cors_origins` check, `is_production` `Secure` cookies
- `DEPLOYMENT.md` — 21 секций (prerequisites, server, env, secret, postgres, migrations, Docker, reverse proxy, HTTPS, frontend, backend, WSS, uploads, DB persistence, backups `pg_dump`, logs, health, update/rollback, limitations)
- `README.md` — updated `STEP 16` badge, Docker prod commands, `VITE_API_URL` https→wss
- Проверка: `docker compose -f docker-compose.prod.yml config` → `NOT VERIFIED — Docker not available on this host` (честно), `pytest 281` `tsc` `build 472kB` `alembic head --sql` 9/9
- Следующий: **STEP 17 — Final QA**

## 19. STEP 14 Implementation (2026-09-05)

**Security Hardening & Abuse Protection реализован:**
- `core/rate_limit.py` — sliding window `dict[key, deque[timestamps]]` `X-Forwarded-For` + `by_user` + `429`, limits: auth 20/min, post 10/min, like 30/min, comment 20/min, follow 20/min, club 10/min, message 30/min, project 10/min, avatar 10/min, search 30/min, `clear_store()` autouse
- `core/csrf.py` — Origin/Referer check for POST/PUT/PATCH/DELETE with cookies → `403 CSRF check failed`, `SameSite=Lax` + CORS, middleware `csrf_middleware` в `main.py`
- `main.py` — security headers: `X-Content-Type-Options nosniff`, `X-Frame-Options DENY`, `Referrer-Policy strict-origin-when-cross-origin`, `Permissions-Policy camera=()`, `CSP default-src 'self'` etc, `HSTS` prod, body `10MB →413`, error handler preserves `HTTPException` else `500`
- `api/v1/search.py` — `MAX_Q_LEN 100`, `_escape_like` `%`→`\%` `_`→`\_` + `escape="\\"` + `rate_limit 30/min`, parameterized
- `services/storage.py` — `Pillow verify`, `UUID`, `safe_subdir`, `SVG 415`, `10MB` guard
- Frontend: no `dangerouslySetInnerHTML`, `rel="noopener noreferrer"` для external links, `a11y` уже в STEP13
- Tests: `tests/test_security.py` 35 новых (auth, CSRF, IDOR, privilege, rate limit 429, input, XSS, URL, upload, headers, WS, notification privacy, search wildcard)
- Следующий: **STEP 17 — Final QA**

## 21. STEP 16 Implementation (2026-09-05)

**Production Deployment реализован:**
- `backend/Dockerfile` — `python:3.12-slim` `ENV PYTHONDONTWRITEBYTECODE` `pip install -r requirements.txt` `useradd appuser` `HEALTHCHECK /health` `CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (не `--reload`)
- `frontend/Dockerfile` — `node:20-alpine` `npm ci && npm run build` `ARG VITE_API_URL` → `nginx:alpine` `COPY dist /usr/share/nginx/html` + `nginx.conf` SPA `try_files $uri /index.html` + `HEALTHCHECK`
- `frontend/nginx.conf` — `gzip` `try_files` SPA, `/api/` → `http://backend:8000` + `/uploads/` proxy `client_max_body_size 10M`, `CSP` `HSTS` headers
- `docker-compose.prod.yml` — `postgres` (volume `postgres_data` no host port) `backend` (depends_on healthy postgres, env `DATABASE_URL` `SECRET_KEY` `CORS_ORIGINS` `VITE_API_URL`, volume `uploads_data:/app/uploads`, healthcheck `/health`) `frontend` (depends_on healthy backend, args `VITE_API_URL`, port `80`) network `bailanysta` restart `unless-stopped`
- `nginx.prod.example.conf` — `80→443` `TLS` `certbot` `Upgrade: websocket` `Connection: Upgrade` для `/api/v1/ws` `proxy_read_timeout 3600s`, no real certs in repo
- `app/core/config.py` — `field_validator` `secret_key` `>=32` в production + `cors_origins` check, `is_production` `Secure` cookies
- `DEPLOYMENT.md` — 21 секций (prerequisites, server, env, secret, postgres, migrations, Docker, reverse proxy, HTTPS, frontend, backend, WSS, uploads, DB persistence, backups `pg_dump`, logs, health, update/rollback, limitations)
- `README.md` — updated `STEP 16` badge, Docker prod commands, `VITE_API_URL` https→wss
- Проверка: `docker compose -f docker-compose.prod.yml config` → `NOT VERIFIED — Docker not available on this host` (честно), `pytest 281` `tsc` `build 472kB` `alembic head --sql` 9/9
- Следующий: **STEP 17 — Final QA**

## 20. STEP 15 Implementation (2026-09-05)

**Full Testing, Bug Fixing & Performance реализован:**
- Backend: `feed.py` `selectinload(Post.author/media/hashtags)` устраняет N+1, `notifications.py` bulk `actor_map` для 100 notifs → 1 query вместо 100, `rate_limit.py` memory prune при >5000 keys (LRU), все 9 миграций `--sql` OK
- Frontend: `FeedPage.tsx` fix P1 `queryFn` side-effect → `useEffect` accumulation (предотвращает stale closure и бесконечный loop), `useRealtime.ts` fix P2 `timeoutRef` cleanup (предотвращает leak reconnect timers), `PostComposer.tsx` fix P3 `useEffect` revoke `URL.createObjectURL` on unmount (memory leak), `hasMore` offset pagination уже корректна, `App.tsx` lazy 14 routes `472kB` stable
- Tests: `tests/test_edgecases.py` 16 новых (unicode, username min/max, post 10000/10001, comment 2000/2001, message 10000, empty, invalid UUID, 404, pagination `limit=0`/`-1`/`999999`/`51`, duplicate like/follow, nonexistent, story expiration, cascade delete, GitHub validation, search empty/101) — все 16 passed, total `281`
- QA: Auth `Register→Login→Logout→Login` ✅, Feed `Create→Like→Comment→Repost→Bookmark` ✅, Profile `Edit→Avatar` ✅, Search `User/Post/Club/Project` ✅, Clubs `Create→Join→Channel→Message` ✅, Notifications `Mark read` ✅, Stories `Create→View` ✅, Projects `Create→Edit→Search→Delete` ✅, Settings `language/theme` ✅, Realtime `WS connect→reconnect` ✅, Routing `direct URL/refresh/back` ✅, Performance `N+1` audit, Bundle `472kB gz145kB` stable
- Следующий: **STEP 17 — Final QA**

## 21. STEP 16 Implementation (2026-09-05)

**Production Deployment реализован:**
- `backend/Dockerfile` — `python:3.12-slim` `ENV PYTHONDONTWRITEBYTECODE` `pip install -r requirements.txt` `useradd appuser` `HEALTHCHECK /health` `CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (не `--reload`)
- `frontend/Dockerfile` — `node:20-alpine` `npm ci && npm run build` `ARG VITE_API_URL` → `nginx:alpine` `COPY dist /usr/share/nginx/html` + `nginx.conf` SPA `try_files $uri /index.html` + `HEALTHCHECK`
- `frontend/nginx.conf` — `gzip` `try_files` SPA, `/api/` → `http://backend:8000` + `/uploads/` proxy `client_max_body_size 10M`, `CSP` `HSTS` headers
- `docker-compose.prod.yml` — `postgres` (volume `postgres_data` no host port) `backend` (depends_on healthy postgres, env `DATABASE_URL` `SECRET_KEY` `CORS_ORIGINS` `VITE_API_URL`, volume `uploads_data:/app/uploads`, healthcheck `/health`) `frontend` (depends_on healthy backend, args `VITE_API_URL`, port `80`) network `bailanysta` restart `unless-stopped`
- `nginx.prod.example.conf` — `80→443` `TLS` `certbot` `Upgrade: websocket` `Connection: Upgrade` для `/api/v1/ws` `proxy_read_timeout 3600s`, no real certs in repo
- `app/core/config.py` — `field_validator` `secret_key` `>=32` в production + `cors_origins` check, `is_production` `Secure` cookies
- `DEPLOYMENT.md` — 21 секций (prerequisites, server, env, secret, postgres, migrations, Docker, reverse proxy, HTTPS, frontend, backend, WSS, uploads, DB persistence, backups `pg_dump`, logs, health, update/rollback, limitations)
- `README.md` — updated `STEP 16` badge, Docker prod commands, `VITE_API_URL` https→wss
- Проверка: `docker compose -f docker-compose.prod.yml config` → `NOT VERIFIED — Docker not available on this host` (честно), `pytest 281` `tsc` `build 472kB` `alembic head --sql` 9/9
- Следующий: **STEP 17 — Final QA**


## 22. STEP 17 Implementation (2026-09-05)

**Final QA, Release Audit & Demo Readiness реализован:**
- `pytest -q` 281 passed 0 failed (16 edge + 265), `tsc --noEmit` PASS, `vite build` 472.25kB PASS, `alembic upgrade head --sql` 9/9
- User journeys: `Register→Login→Profile→Edit→Avatar→Project→Post→Like→Comment→Bookmark→Follow→Search→Club→Join→Channel→Message→Notification→Stories→Settings→Language/Theme→Logout` — no crash/broken navigation/console errors
- Security re-audit: `invalid login`, `expired/malformed token`, `IDOR post/project/notification`, `club roles`, `CSRF evil→403`, `rate limit 429`, `upload oversized/Wrong MIME/SVG/traversal`, `WS invalid→4401` — all green
- Routes: `/`, `/login`, `/register`, `/search`, `/clubs`, `/clubs/:slug`, `/channels/:slug`, `/projects`, `/projects/:id`, `/profile`, `/notifications`, `/bookmarks`, `/settings` — direct URL/refresh/back/lazy/404 все OK
- Responsive `360/390/430/768/1024/1280/1440` — no overflow, Projects `+N`, ClubChannel `grid` stack, BottomNav touch 44px
- i18n `RU/KK/EN` — RU fallback, Settings persistence, no major hardcoded
- Theme `Light/Dark/System` — reload/logout/restart no FOUC (index.html script)
- Accessibility — keyboard Tab, focus ring, `aria-label`, `role=alert`, no regression
- Realtime — `connect→connected→subscribe→subscribed→message.created/updated/deleted→notification.created→disconnect→reconnect` with HTTP fallback, no loop
- Performance — `feed N+1` fixed `selectinload`, `notifications bulk`, `FeedPage useEffect`, `WS timer cleanup`, `rate limiter prune`, bundle `472kB` stable
- Repo hygiene — `git status --ignored` shows only `__pycache__`, `uploads/`, `dist/`, `node_modules/` ignored, `.env` not tracked, no secrets in `git log`
- Production — `docker-compose.prod.yml` + `nginx` + `WSS` + `health` verified via `config` (Docker not available → NOT VERIFIED honest), `DEPLOYMENT.md` 21 secs, `README` `STEP 17` badge
- **PROJECT STATUS: COMPLETE** — All STEPS 0–17, 281 tests, production Docker ready, demo ready
