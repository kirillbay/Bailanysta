# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 4 — Profiles)

---

## 1. Текущий STEP

**STEP 4 — Profiles — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 4 — profiles` (см. §17)
- Статус: публичный профиль, own PATCH, avatar/cover upload + static, frontend ProfilePage — всё работает, 57 тестов зелёных

**Последний завершённый STEP:** STEP 4 — Profiles (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 5 — Posts & Media

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |
| 0+ | Persistent Protocol setup | 2026-09-05 | `2d5e1d3` | ✅ Done |
| 1 | Foundation | 2026-09-05 | `7619de1` | ✅ Done |
| 2 | Database Foundation | 2026-09-05 | `d324979` | ✅ Done |
| 3 | Authentication | 2026-09-05 | `c291114` | ✅ Done |
| 4 | Profiles | 2026-09-05 | `feat STEP4` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts & Media → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Vite + AuthProvider + ProfilePage] → [Backend: FastAPI /api/v1/users/* + /uploads static + storage] → [PostgreSQL 16 + SQLite test]
                         ↕ credentials:include, HttpOnly cookie
                         ↕ TanStack Query (me + public profile + mutation + upload)
```

- Frontend: `api/users.ts` (me/public/patch/uploadAvatar/Cover, resolveUrl), `pages/ProfilePage.tsx` (cover+avatar, edit form RHF+Zod, preview, upload), `App.tsx` /profile + /profile/:username
- Backend: `app/core/config.py` (upload_dir, max_avatar/cover 5 MB), `app/services/storage.py` (Pillow verify, UUID filenames, subdir sanitize, size+MIME), `app/schemas/user.py` (UserPublic/UserRead/UserUpdate), `app/api/v1/users.py` (5 endpoints), `app/main.py` mount `/uploads` StaticFiles
- Storage: local `UPLOAD_DIR=./uploads` (gitignored), S3 placeholder в .env.example
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Users API: `api/users.ts` me/public/update/uploadAvatar/uploadCover + resolveUrl (API_URL prefix)
- Profile: `pages/ProfilePage.tsx` — cover gradient + avatar (fallback initial), display_name/bio/created_at, own edit toggle (display_name 100, bio 500 Zod), upload buttons (accept jpeg/png/webp, preview via URL.createObjectURL, loading state, msg, invalidate queries), future posts card
- Routing: `App.tsx` `/profile` + `/profile/:username` protected via RequireAuth+AppShell
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.25s, 458.08 kB js gzip 141.60 kB (17.77 kB css), 1685 modules

---

## 5. Backend Status

- Статус: **runnable ✅**
- Deps: `requirements.txt` + `Pillow==11.1.0` + `python-multipart==0.0.9` — установлены
- Core: `config.py` + `upload_dir`, `max_avatar/cover 5`; `services/storage.py` (ALLOWED_MIME jpeg/png/webp, MAX_MB 5, _validate_size 413, _detect_and_validate via Pillow verify + format→ext, save_image UUID hex, safe_subdir, public_url `/uploads/...`)
- Schemas: `schemas/user.py` — `UserPublic` (id,username,display_name,bio,avatar/cover,created_at) no email/hash, `UserRead` full, `UserUpdate` display_name 100 bio 500
- API: `api/v1/users.py` — `GET /users/me` 200 protected, `PATCH /users/me` 200 (only own, strip, commit), `GET /users/{username}` 200 public 404, `POST /users/me/avatar` 200 (auth, read file, empty 400, save_image avatars), `POST /users/me/cover` 200 (covers)
- Static: `app/main.py` — `Path(upload_dir).mkdir` + `mount /uploads StaticFiles`, upload dir gitignored
- Tests: `test_profiles.py` 18 passed, total 57 passed (25 auth + 8 db + 6 health + 18 profiles)
- Startup: routes `/api/v1/users/*` + `/uploads` verified

---

## 6. Database Status

- Статус: **unchanged ✅** (users model already has avatar_url, cover_url, display_name, bio)
- Migrations: `001_create_users` — no new migration (полей достаточно, не создавали ненужную)

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |

- No migration for STEP4

---

## 8. Authentication Status

- Статус: **unchanged ✅** (Argon2id, JWT HttpOnly, etc — STEP3)
- Profiles использует `get_current_user` — ownership только own

---

## 9. Implemented Features

> STEP 4 — profiles done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, SQLAlchemy, Alembic, User model
- [x] Auth — register/login/me/logout + JWT
- [x] Profiles: public GET, own GET/PATCH, avatar/cover upload + storage + frontend ProfilePage
- [ ] Posts — STEP5
- [ ] Feed — STEP6
- [ ] Stories — STEP8
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 458 kB
- Backend: Render/Railway — uploads local MVP (documented S3 later), health/db
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **57 passed** (25 auth + 8 db + 6 health + 18 profiles) ✅
  - profiles: public 3 (success no email/hash, 404, no jwt leak), own 2, update 4 (own success, 422 bio, no IDOR 404/405, unauth 401), uploads 8 (avatar/cover success + static serve, unauth 401, unsupported 415, oversized 413, malicious filename safe, safe filename unique, no traversal, email leak after update)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.25s
- Integration: `Register/Login → Profile → Edit → Upload → refresh` manual via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- Uploads локальные (`./uploads`) — MVP documented, S3 abstraction `services/storage.py` готова к замене (см. Known Issues в DEVLOG)
- No username editing (оставлен immutable — ARCHITECTURE)
- No avatar/cover delete endpoint — можно перезаписать upload
- Docker absence still — PG not runnable locally

---

## 13. Technical Debt

- Добавить S3-compatible storage (STEP16) — заменить LocalStorage via service abstraction
- Добавить image resize/compression (сейчас только verify + save original)
- Добавить `DATABASE_URL_TEST` PG tests (сейчас SQLite in-memory for auth/profiles)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP5.

---

## 15. Next Recommended STEP

**STEP 5 — Posts & Media**

- `posts` model + migration, `POST /posts` (text+hashtags+mentions), media via storage, tests, frontend composer

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Storage `services/storage.py` локально + Pillow verify | Безопасность (MIME+content), S3 позже без ломки API |
| 2026-09-05 | UUID hex filenames + safe_subdir + no user path | No path traversal, no overwrite |
| 2026-09-05 | UserPublic без email/hash/JWT | Privacy, SECURITY.md |
| 2026-09-05 | PATCH /users/me только own (no IDOR) | Security ownership via get_current_user |
| 2026-09-05 | Static /uploads mount | Простая отдача, не code execution |
| 2026-09-05 | Frontend ProfilePage с preview + optimistic invalidate | UX, TanStack Query |

---

## 17. Последний Git Commit

```
feat: STEP 4 — profiles (предстоит)
Branch: main | Status: clean (после commit)
Profiles: users API, storage, uploads, ProfilePage, 18 tests
```

---

## 18. Изменённые файлы (STEP 4)

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
