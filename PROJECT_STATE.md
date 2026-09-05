# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 12 — Projects & Developer Showcase)

---

## 1. Текущий STEP

**STEP 12 — Projects & Developer Showcase — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 12 — projects and developer showcase` (см. §17)
- Статус: Project model 009 + showcase CRUD + image upload + profile tabs + search projects + ProjectsPage/Detail — 230 тестов зелёных, showcase без GitHub API

**Последний завершённый STEP:** STEP 12 — Projects & Developer Showcase (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 13 — i18n/Theme/Responsive

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |
| 0+ | Persistent Protocol setup | 2026-09-05 | `2d5e1d3` | ✅ Done |
| 1 | Foundation | 2026-09-05 | `7619de1` | ✅ Done |
| 2 | Database Foundation | 2026-09-05 | `d324979` | ✅ Done |
| 3 | Authentication | 2026-09-05 | `c291114` | ✅ Done |
| 4 | Profiles | 2026-09-05 | `197ed2c` | ✅ Done |
| 5 | Posts & Media | 2026-09-05 | `a8b2f66` | ✅ Done |
| 6 | Feed & Social Interactions | 2026-09-05 | `040794b` | ✅ Done |
| 7 | Follow, Search & Hashtags | 2026-09-05 | `831f9b9` | ✅ Done |
| 8 | Stories | 2026-09-05 | `79bd004` | ✅ Done |
| 9 | Clubs, Members & Roles | 2026-09-05 | `1b83af6` | ✅ Done |
| 10 | Club Channels & Messaging | 2026-09-05 | `5973415` | ✅ Done |
| 11 | Notifications & Realtime | 2026-09-05 | `e9008ad` | ✅ Done |
| 12 | Projects & Developer Showcase | 2026-09-05 | `feat STEP12` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories ✅ → 9 Clubs ✅ → 10 Channels/Messaging ✅ → 11 Notifications/Realtime ✅ → 12 Projects ✅ → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
                    ┌───────────────┐
                    │    React      │  AppShell + Feed + Projects + Profile Tabs
                    └───────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
              HTTP REST            WebSocket (/api/v1/ws)
                 │                     │
                 └──────────┬──────────┘
                            │
                      FastAPI Backend
                            │
                 ┌──────────┴──────────┐
                 │                     │
             PostgreSQL          Realtime Manager (in-memory)
                 │                     │
           notifications+projects  channel_subscribers + user_connections
```

```
Club
 ├── ClubMember
 ├── ClubChannel
 │    └── ClubMessage  (realtime broadcast)
User
 ├── Notification (follow/like/comment)
 └── Project (showcase, technologies, github/demo, image, status/position)
Project
 ├── owner (User)
 ├── technologies (JSON array)
 ├── github_url/demo_url (validated URL)
 └── image (uploads/projects)
```

- Frontend: `api/projects.ts` (listUser/listMy/get/create/update/delete/uploadImage), `components/ProjectCard.tsx` + `ProjectForm.tsx` (chips, max 20, 50 chars, dedup), `pages/ProjectsPage.tsx` (/projects global my), `pages/ProjectDetailPage.tsx` (/projects/:id), `pages/ProfilePage.tsx` Projects|Posts tabs + inline create/edit/delete/upload, `pages/SearchPage.tsx` projects type, `App.tsx` /projects + /projects/:id
- Backend: `models/project.py` (id, owner_id FK CASCADE, name 150, description Text, technologies JSON, github/demo/image 512, status idea/in_progress/completed/archived, position int, created/updated, indexes owner, owner+position, owner+created), `alembic 009_create_projects`, `schemas/project.py` (ProjectCreate/Update/Read + URL/tech validation), `api/v1/projects.py` (GET /users/{username}/projects public, GET /users/me/projects auth, GET /projects/{id} public, POST/PATCH/DELETE /users/me/projects auth owner only, POST /users/me/projects/{id}/image owner only, position auto max+1, no owner_id forgery), `api/v1/search.py` + projects ILIKE name/desc/tech, `services/storage.py` reuse save_image projects/
- Детали → `ARCHITECTURE.md` §17 (projects diagram + showcase note), `SECURITY.md` §17 (ownership/URL/upload)

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Projects: `api/projects.ts` + `components/ProjectCard.tsx` (image or gradient, name, status badge, desc, tech badges, GitHub/Demo external links, owner link) + `components/ProjectForm.tsx` (RHF Zod name 150/desc 2000/tech chips dedup 20×50/github host demo URL status enum + confirmation delete) + `pages/ProjectsPage.tsx` (/projects my list + create/edit/delete/upload image no reload) + `pages/ProjectDetailPage.tsx` (/projects/:id public) + `pages/ProfilePage.tsx` tabs Posts|Projects (public list, empty states No projects yet / This developer hasn't added..., own Add project) + `pages/SearchPage.tsx` projects tab (ILIKE name/desc/tech), `App.tsx` routes /projects & /projects/:id
- Notifications+Realtime: `api/notifications.ts`, `hooks/useRealtime.ts`, `NotificationsPage`, `ClubChannelPage` WS badge still
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.08s, 1712 modules, 526.96 kB js gzip 155.73 kB (18.88 kB css) — chunks >500kB warning

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/project.py` — id UUID PK, owner_id FK CASCADE index, name 150, description Text, technologies JSON default [], github_url/demo_url/image_url 512 nullable, status 20 default idea, position int, created/updated, indexes owner+position, owner+created
- Schemas: `schemas/project.py` — ProjectCreate/Update/Read, ALLOWED_STATUSES idea/in_progress/completed/archived, MAX_TECH 20 MAX_TECH_LEN 50 dedup lower, ALLOWED_GITHUB_HOSTS github.com/www.github.com, _validate_url scheme https/http reject javascript/data/file
- Migration: `alembic/versions/009_create_projects.py` — projects — `--sql` verified
- APIs: `api/v1/projects.py` — `GET /users/{username}/projects` public 404, `GET /users/me/projects` auth, `GET /projects/{id}` public 404, `POST /users/me/projects` 201 owner=current_user position max+1, `PATCH /users/me/projects/{id}` owner 403, `DELETE` owner 403 best-effort file unlink, `POST .../image` owner 403 Pillow via save_image projects/ 5MB UUID no traversal; `api/v1/search.py` + projects ILIKE name/description/cast(technologies as String) limit 50
- Notifications+Realtime: `models/notification.py`, `008_create_notifications`, `services/notifications.py`, `api/v1/notifications.py` + `realtime/manager.py` + `api/v1/realtime.py` unchanged
- Router: `router.py` + projects + search projects
- Tests: `test_projects.py` 24 passed, total 230 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels + 10 notifications + 11 realtime + 24 projects)
- Startup: routes `/projects`, `/users/*/projects`, `/search` verified

---

## 6. Database Status

- Статус: **projects added ✅**
- Tables: `projects` + `notifications` + previous 13 + `users` (14 tables total)
- Indexes: `ix_projects_owner_id`, `ix_projects_owner_position`, `ix_projects_owner_created`
- Constraints: FK CASCADE owner_id → users.id, status validated via Pydantic (no DB enum to keep SQLite compat)

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |
| 002_create_posts | create posts + media + hashtags | 2026-09-05 | ✅ Created, --sql OK |
| 003_create_social | create social interactions | 2026-09-05 | ✅ Created, --sql OK |
| 004_create_follows | create follows | 2026-09-05 | ✅ Created, --sql OK |
| 005_create_stories | create stories | 2026-09-05 | ✅ Created, --sql OK |
| 006_create_clubs | create clubs | 2026-09-05 | ✅ Created, --sql OK |
| 007_create_club_channels_messages | create club channels and messages | 2026-09-05 | ✅ Created, --sql OK |
| 008_create_notifications | create notifications | 2026-09-05 | ✅ Created, --sql OK |
| 009_create_projects | create projects | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → all 9 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- WS auth via same `decode_token` (cookie `access_token` HttpOnly or `?token=`), `is_active`, `type==access`, close 4401, no user_id forgery, no second auth system

---

## 9. Implemented Features

> STEP 12 — projects done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow/Search — follow, search, hashtags
- [x] Stories — 24h image/video/text, grouped feed, viewer
- [x] Clubs — create, list/search, detail, join/leave, members, roles, avatar/cover
- [x] Channels/Messaging — ClubChannel + ClubMessage, 9 endpoints, ClubChannelPage + realtime
- [x] Notifications — model/service/API + triggers + WS badge
- [x] Realtime — manager + /ws auth + broadcast
- [x] Projects — model 009, showcase CRUD, image upload projects/, status enum, tech dedup, GitHub/demo URL validation, public/user/my endpoints, search projects ILIKE, frontend tabs/cards/forms/detail, ownership 403, position ordering
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 527 kB, projects showcase ready
- Backend: Render/Railway — projects showcase ready, uploads/projects, manager in-memory (no Redis)
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **230 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels + 10 notifications + 11 realtime + 24 projects) ✅
  - projects 24 (create/list own+public/get/update/delete/pagination, empty/long name/desc/status/tech length/too many/dedup, invalid URL scheme/github host, unauth, cannot update/delete/upload other, forged owner ignored, sensitive, image success/415/401, search name/desc/tech)
  - notifications 10, realtime 11
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.08s
- Integration: `login → create project → list own/public → patch/delete 403 other → upload image → search projects` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No Redis — manager in-memory, single instance only (debt)
- No private DMs (future)
- No voice/video (future)
- No reactions/threads (future)
- No file attachments in messages (future)
- Hashtag/Project ILIKE search, Bookmarks 50 (known)
- Frontend chunks >500kB warning (527 kB)
- No drag&drop project reorder (position auto, debt)

---

## 13. Technical Debt

- Add Redis Pub/Sub for multi-instance scaling (debt, not now per spec §2)
- Add S3 (долг, projects uploads local)
- Add cursor pagination for feed/search/notifications/projects (offset now)
- Add WebSocket presence/typing (future)
- Version single source (долг)
- Project drag&drop reorder via position (future)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP13.

---

## 15. Next Recommended STEP

**STEP 13 — i18n/Theme/Responsive**

- polish i18n completeness, theme audit, responsive QA, accessibility

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Notification model recipient+actor+type+entity, indexes recipient+created/read | Spec §3, performance |
| 2026-09-05 | Service `create_notification` + `notify_follow/like/comment` centralized, no self, ALLOWED_TYPES | Spec §6, no spread |
| 2026-09-05 | Follow/like/comment triggers notify + `manager.send_to_user` after DB commit | Spec §7, ghost-free |
| 2026-09-05 | Manager in-memory `user_connections` + `channel_subscribers` + Lock, no Redis | Spec §2, MVP |
| 2026-09-05 | WS auth via same `decode_token` (cookie or ?token), 4401 close, no second auth | Spec §9, no forgery |
| 2026-09-05 | Channel subscribe checks `ClubChannel` exists + `ClubMember` membership, IDOR via club | Spec §10, security |
| 2026-09-05 | Events `connected/subscribed/message.created|updated|deleted/notification.created/error` JSON | Spec §11, structured |
| 2026-09-05 | Message flow DB commit before broadcast, dedup via message.id | Spec §12-13 |
| 2026-09-05 | Frontend `useChannelRealtime` with backoff 1s→16s, `useNotificationsRealtime`, HTTP fallback | Spec §14-16 |
| 2026-09-05 | Migration 008 separate | Not rewrite old |
| 2026-09-05 | No Redis/Kafka per spec §2, documented debt | Keep MVP simple |
| 2026-09-05 | Project JSON technologies, max 20×50 dedup lower, URL validation https/http github host, status enum | Spec §1-4, MVP showcase no taxonomy |
| 2026-09-05 | Project position max+1, no drag&drop yet | Spec §17, debt |
| 2026-09-05 | Storage reuse saves to uploads/projects/ UUID no traversal | Spec §5, S3 debt |
| 2026-09-05 | Migration 009 separate | Not rewrite 001-008 |
| 2026-09-05 | No GitHub API/OAuth yet, only showcase links | Spec §24 |

---

## 17. Последний Git Commit

```
feat: STEP 12 — projects and developer showcase
Branch: main | Status: clean (после commit)
Projects: model 009, 6+1 endpoints, showcase + image upload + search, Profile tabs + ProjectsPage/Detail, 24 tests, 230 total
GitHub API/OAuth НЕ реализовывались — только showcase + github/demo links
```

---

## 18. Изменённые файлы (STEP 12)

```
[new] backend/app/models/project.py
[mod] backend/app/models/__init__.py (+ Project)
[new] backend/alembic/versions/009_create_projects.py
[new] backend/app/schemas/project.py
[new] backend/app/api/v1/projects.py
[mod] backend/app/api/v1/router.py (+ projects)
[mod] backend/app/api/v1/search.py (+ projects ILIKE)
[new] backend/app/tests/test_projects.py (24 tests)
[new] frontend/src/api/projects.ts
[new] frontend/src/components/ProjectCard.tsx
[new] frontend/src/components/ProjectForm.tsx
[new] frontend/src/pages/ProjectsPage.tsx
[new] frontend/src/pages/ProjectDetailPage.tsx
[mod] frontend/src/pages/ProfilePage.tsx (+ Projects|Posts tabs, inline CRUD)
[mod] frontend/src/pages/SearchPage.tsx (+ projects tab)
[mod] frontend/src/api/search.ts (+ projects)
[mod] frontend/src/App.tsx (+ /projects, /projects/:projectId)
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
