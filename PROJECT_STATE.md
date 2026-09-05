# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 1 — Foundation)

---

## 1. Текущий STEP

**STEP 1 — Foundation — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 1 — foundation` (см. §17)
- Статус: frontend + backend реально запускаются, интегрированы, build/tests зелёные

**Последний завершённый STEP:** STEP 1 — Foundation (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 2 — Database (модели, Alembic, Postgres)

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |
| 0+ | Persistent Protocol setup | 2026-09-05 | `2d5e1d3` | ✅ Done |
| 1 | Foundation | 2026-09-05 | `feat STEP1` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database → 3 Authentication → 4 Profiles → 5 Posts & Media → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Vite @ :5173] → [Backend: FastAPI @ :8000 /api/v1/*] → [PostgreSQL + Storage (planned)]
                     ↕ i18next (ru/kk/en)              ↕ CORS + security headers
                     ↕ TanStack Query                  ↕ JSON errors, /health
```

- Frontend: `React 18 + TS + Vite 6 + Tailwind 3 + shadcn-like ui + Lucide + React Router 6 + TanStack Query 5 + RHF + Zod + i18next 24` — роутер с layout, AppShell, 9 заглушек-страниц
- Backend: `FastAPI 0.115 + pydantic-settings + SQLAlchemy 2.x (installed) + Alembic` — `main.py` с CORS + headers + `/api/v1/health` + `/health` + `/`
- API versioning: `/api/v1` префикс, агрегирующий router
- Детали → `ARCHITECTURE.md` (обновляется по необходимости)

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Deps установлены (152 packages), `@types/node` для vite.config
- Config: `vite.config.ts` (alias `@`→`src`), `tsconfig.json` + `tsconfig.node.json` (composite), `tailwind.config.js`, `postcss.config.js`, `index.html`
- Core: `src/lib/utils.ts` (cn), `src/lib/i18n.ts` (detector localStorage→navigator, 3 языка), `src/api/client.ts` (fetch wrapper, VITE_API_URL, credentials include), `src/hooks/useHealth.ts` (TanStack Query), `src/stores/theme.tsx` (light/dark/system + localStorage), `src/components/ErrorBoundary.tsx`
- UI: `components/ui/{button,card,badge,skeleton}` — shadcn-стиль, `components/layout/AppShell.tsx` — Sidebar (desktop) + BottomNav (mobile) + TopBar
- Pages: `FeedPage.tsx` (hero + health-check интеграция + skeleton demo), `PlaceholderPage.tsx` (для 8 роутов), `NotFoundPage.tsx`
- Routing: `App.tsx` — `createBrowserRouter` с 9 routes: `/`, `/explore`, `/search`, `/clubs`, `/projects`, `/messages`, `/notifications`, `/profile`, `/settings` + `*` 404
- i18n: подключён в `main.tsx`, переключатель в Sidebar, `locales/{ru,kk,en}.json` используются через `t()`
- Theme: провайдер в `main.tsx`, переключатель light/dark/system в Sidebar
- Build: `npm run build` ✅ (17.19s, 354.82 kB js gzip 113 kB, 15.29 kB css), `tsc --noEmit` ✅
- Dev: `npm run dev` на :5173, `npm run preview` на :4173 проверен

---

## 5. Backend Status

- Статус: **runnable ✅**
- Deps: `requirements.txt` (fastapi, uvicorn[standard], pydantic, pydantic-settings, sqlalchemy, alembic, httpx, pytest, anyio) — установлены
- Core: `app/core/config.py` (BaseSettings, CORS list, is_production), `app/main.py` (FastAPI, CORSMiddleware, security headers middleware, global error handler, routers)
- API: `app/api/v1/health.py` (`GET /health` → `{status,service,version,env}`), `app/api/v1/router.py` (aggregate), prefix `/api/v1`
- Root: `GET /` и `GET /health` (для LB)
- Config: `pytest.ini`, `.env.example` уже есть, `VITE_API_URL` отделена
- Tests: `app/tests/test_health.py` (6 tests: root, v1 health, CORS, headers, 404) — все ✅
- Startup: `uvicorn app.main:app --host 127.0.0.1 --port 8000` ✅, `curl /api/v1/health` → `{"status":"ok"}`
- Headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy` ✅

---

## 6. Database Status

- Статус: **не создана** (ожидается STEP 2)
- Engine: не настроен (SQLAlchemy установлена, но Base/engine не созданы)
- Migrations: 0
- Seed data: нет

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| — | (нет) | — | — |

---

## 8. Authentication Status

- Статус: **не реализовано** (план STEP 3)
- План: Argon2id + JWT cookies HttpOnly SameSite + CSRF

---

## 9. Implemented Features

> STEP 1 — только foundation, бизнес-фичи — заглушки.

- [x] Foundation: frontend shell + routing + i18n + theme + error handling
- [x] Foundation: backend health + CORS + headers
- [x] Foundation: Frontend ↔ Backend integration (health check via Query)
- [ ] Auth (register/login/logout/me) — STEP 3
- [ ] Profiles — STEP 4
- [ ] Posts + media — STEP 5
- [ ] Feed — STEP 6
- [ ] Stories — STEP 8
- [ ] Clubs — STEP 9
- [ ] Messaging — STEP 10
- [ ] Notifications — STEP 11
- [ ] Projects — STEP 12
- [x] i18n skeleton (ru/kk/en) + switcher — STEP 1 done, polish STEP 13
- [x] Dark/Light/system theme — STEP 1 done, polish STEP 13

---

## 10. Deployment Status

- Frontend hosting: не выбран (кандидат Vercel) — preview build готов
- Backend hosting: не выбран (Render/Railway/Fly) — health ready
- Database hosting: не выбран (Neon/Supabase)
- Domain: нет
- CI/CD: нет

---

## 11. Tests Status

- Backend: `pytest app/tests/test_health.py -v` → **6 passed in 0.76s** ✅
- Frontend: `tsc --noEmit` → ✅, `npm run build` → ✅ (17.19s)
- Integration: `Backend :8000 /api/v1/health` → ok, `Frontend :4173 /` → 200 + contains Bailanysta ✅
- Coverage: не измерялась (STEP 15)

---

## 12. Known Issues

- Нет критических. Незначительные:
  - `npm audit` — 2 moderate (esbuild, не критично для MVP)
  - `frontend/dist/` генерится при build, gitignored — ок
  - Backend `database_url` пока sqlite placeholder, реальная БД — STEP 2
  - No `docker-compose.yml` ещё (опционально, будет STEP 2)

---

## 13. Technical Debt

- Добавить `eslint` config (сейчас скрипт есть, но конфига нет) — low
- Вынести `version` в единый source (frontend + backend дублируют "0.1.0")
- Добавить `vite` proxy для dev чтобы избежать CORS в некоторых окружениях (сейчас CORS настроен, но proxy — удобство)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP 2.

---

## 15. Next Recommended STEP

**STEP 2 — Database**

- Создать `app/database/base.py` (Base, engine, session), `alembic` init, `users` модель (минимально для auth)
- Первая миграция, `docker-compose.yml` для Postgres (опционально)
- Тесты на DB connection

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Frontend scaffold Vite 6 + React 18 + TS 5.6 | Быстрый foundation |
| 2026-09-05 | Tailwind + shadcn-like ui primitives вручную (button/card/badge/skeleton) вместо CLI | Минимум зависимостей, STEP 1 не раздувать |
| 2026-09-05 | Theme via custom context + localStorage + matchMedia (без next-themes) | Проще, без лишней зависимости |
| 2026-09-05 | Backend CORS из `cors_origins` string → list property | Совместимо с .env comma-list |
| 2026-09-05 | Security headers middleware в main.py (nosniff, DENY, Referrer-Policy) | SECURITY.md §6 |
| 2026-09-05 | API client — native fetch (не axios) + credentials include | Меньше deps, достаточно для MVP |

---

## 17. Последний Git Commit

```
73041d8 feat: STEP 1 — foundation (frontend vite+react+router+i18n+theme+query+shell+health integration, backend fastapi+health+cors+headers+tests) — 2026-09-05
Branch: main | Status: clean | Remote: не настроен
37 files, +4490 -98
```

---

## 18. Изменённые файлы (STEP 1)

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
[new] frontend/src/components/ui/{button,card,badge,skeleton}.tsx
[new] frontend/src/components/layout/AppShell.tsx
[new] frontend/src/pages/{FeedPage,PlaceholderPage,NotFoundPage}.tsx
[new] backend/requirements.txt
[new] backend/pytest.ini
[new] backend/app/core/config.py
[new] backend/app/main.py
[new] backend/app/api/v1/{health,router}.py
[new] backend/app/database/base.py (placeholder)
[new] backend/app/tests/test_health.py
[mod] frontend/tsconfig.node.json — composite fix
```

---

## 19. Как восстанавливать контекст (New Chat Recovery)

1. Найти workspace `C:\Users\lueex\Desktop\Bailanysta`
2. Прочитать `MASTER_PROMPT.md`
3. Прочитать этот `PROJECT_STATE.md`
4. Прочитать `ARCHITECTURE.md` + `SECURITY.md`
5. Прочитать последние записи `DEVELOPMENT_LOG.md`
6. Проверить `git status` + `git log --oneline -5`
7. Проверить структуру `frontend/` и `backend/`
8. Определить последний завершённый STEP и следующий → ждать команды
