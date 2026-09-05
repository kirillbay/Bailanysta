# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 9 — Clubs, Members & Roles)

---

## 1. Текущий STEP

**STEP 9 — Clubs, Members & Roles — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 9 — clubs and members` (см. §17)
- Статус: Clubs CRUD + join/leave + members + roles/permissions + Club pages — 170 тестов зелёных

**Последний завершённый STEP:** STEP 9 — Clubs, Members & Roles (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 10 — Club Channels & Messaging

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
| 9 | Clubs, Members & Roles | 2026-09-05 | `feat STEP9` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories ✅ → 9 Clubs ✅ → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: Clubs list + Club page + create + members + role UI] → [Backend: /clubs CRUD + join/leave + members + role mgmt + avatar/cover] → [Postgres 006_clubs + SQLite test]
                         ↕ clubsApi, TanStack Query clubs/members
```

- Frontend: `api/clubs.ts` (list/get/create/update/remove/join/leave/members/updateRole/removeMember/uploadAvatar/Cover), `pages/ClubsPage.tsx` (search, create form Zod, cards, pagination), `pages/ClubPage.tsx` (cover/avatar, join/leave, edit, delete, members list with role badge + select + remove, Channels placeholder, avatar/cover upload), `App.tsx` /clubs + /clubs/:slug
- Backend: `models/club.py` (Club, ClubMember + slugify, roles owner/admin/moderator/member), `alembic 006_create_clubs`, `schemas/club.py`, `api/v1/clubs.py` (12 endpoints + permission matrix), `services/storage.py` reuse for clubs/avatars covers
- DB: `006_create_clubs` added clubs + club_members
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Clubs: `pages/ClubsPage.tsx` — header Create Club, search q, create form name 2-100 description 2000, cards avatar initials + name/slug/members_count/role badge + description, skeleton/empty/error, load more
- Club: `pages/ClubPage.tsx` — cover gradient + avatar initials, name/slug/members/owner, description, role badge, Join/Leave (owner cannot leave), Edit (owner/admin), Delete (owner), avatar/cover upload (clubs/avatars|covers), Channels placeholder (general/announcements), members list (avatar, username, role, joined, role select + remove per permission)
- APIs: `api/clubs.ts` all 12 endpoints + resolve not needed (avatar url direct)
- Routing: `App.tsx` `/clubs` + `/clubs/:slug` protected, placeholder removed
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 4.03s, 1702 modules, 496.44 kB js gzip 149.61 kB (17.13 kB css)

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/club.py` — `Club` (UUID PK, owner_id FK CASCADE index, name 100, slug 100 unique index, description Text, avatar/cover 512 nullable, created/updated server_default now, owner joined), `ClubMember` (UUID PK, club_id FK CASCADE index, user_id FK CASCADE index, role 20, joined_at, Unique club+user, index)
- Schemas: `schemas/club.py` — ClubCreate 2-100 + description 2000, ClubUpdate, ClubRead (members_count, is_member, role), MemberRead
- Migration: `alembic/versions/006_create_clubs.py` — clubs + club_members — `--sql` verified
- APIs: `api/v1/clubs.py` — `POST /clubs` 201 (auth, slugify name, unique slug with counter, creator owner), `GET /clubs?q&limit&offset` public 50, ILIKE name/slug/description, `GET /clubs/{slug}` public with members_count + is_member/role via Request cookie optional decode, `PATCH /clubs/{slug}` 200 (owner/admin), `DELETE` 204 (owner only, cascade), `POST /join` 201 idempotent, `DELETE /leave` 204 owner cannot leave 400, `GET /members` paginated `members_count`, `PATCH /members/{username}/role` (owner can all, admin cannot owner/admin/assign admin, cannot owner), `DELETE /members/{username}` (owner any, admin not admin, moderator only member), `POST /avatar|cover` (owner/admin, save_image clubs/avatars|covers)
- Permissions: ROLE_RANK member1<moderator2<admin3<owner4, matrix enforced backend, no privilege escalation
- Tests: `test_clubs.py` 23 passed, total 170 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs)
- Startup: routes `/clubs`, `/clubs/{slug}`, `/join`, `/members` etc verified

---

## 6. Database Status

- Статус: **clubs added ✅**
- Tables: `clubs`, `club_members` + previous 11 + `users`
- Indexes: `ix_clubs_owner_id`, `ix_clubs_slug`, `ix_club_members_club_id`, `ix_club_members_user_id`, `ix_club_members_club_user`
- Constraints: Unique slug, Unique club+user, FK CASCADE

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

- `alembic upgrade head --sql` → all 6 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- Clubs mutations require auth, role checks, IDOR prevented

---

## 9. Implemented Features

> STEP 9 — clubs done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow/Search — follow, search, hashtags
- [x] Stories — 24h image/video/text, grouped feed, viewer
- [x] Clubs: create (slugify), list/search, detail with members_count/is_member/role, patch owner/admin, delete owner, join/leave (owner cannot leave), members list paginated, role mgmt (owner>admin>moderator>member, no escalation), avatar/cover upload, frontend list+create+detail+members
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 496 kB, clubs ready
- Backend: Render/Railway — clubs ready, uploads clubs/
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **170 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs) ✅
  - clubs 23 (create 1, unauth 1, owner auto 1, public list/detail 1, pagination/search 1, edit owner 1, edit unauth 403, delete owner/non-owner 2, nonexist 404, join/dup 1, leave/dup 1, owner cannot leave 400, members list 1, owner role 1, promote/demote 1, admin perms 3, moderator perms 1, member forbidden 2, cannot promote to owner 1, cannot modify owner 1, privilege escalation 1, forged owner_id 1, sensitive fields)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 4.03s
- Integration: `register → create club → detail → join → members → promote → search → edit → delete` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No channels/messages (STEP10)
- No clubs search beyond ILIKE (MVP)
- No club ownership transfer (future)
- No club invite system (future)
- Hashtag ILIKE, Bookmarks 50 (known)

---

## 13. Technical Debt

- Add S3 (долг)
- Add clubs avatar/cover resize (долг)
- Add cursor pagination for clubs/members (offset)
- Add club settings page separate (currently inline)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP10.

---

## 15. Next Recommended STEP

**STEP 10 — Club Channels & Messaging**

- club_channels model, channel CRUD, club_messages with realtime MVP (polling/WebSocket), club page channels UI

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Club slugify lower + regex + counter unique | Spec §1, human URL |
| 2026-09-05 | Roles owner/admin/moderator/member with RANK 1-4 | Spec §2-3, matrix |
| 2026-09-05 | Owner auto member on create | Spec §2 |
| 2026-09-05 | Permission matrix owner>admin>moderator (admin cannot owner, moderator only member) | Spec §3/7, no escalation |
| 2026-09-05 | Owner cannot leave without transfer 400 | Spec §5 |
| 2026-09-05 | Clubs search ILIKE name/slug/description | Spec §14, no ES |
| 2026-09-05 | Storage reuse clubs/avatars|covers | Spec §9, safe |
| 2026-09-05 | Migration 006 separate | Not rewrite old |

---

## 17. Последний Git Commit

```
feat: STEP 9 — clubs and members (предстоит)
Branch: main | Status: clean (после commit)
Clubs: models 006, 12 endpoints, permission matrix, ClubsPage/ClubPage, 23 tests
```

---

## 18. Изменённые файлы (STEP 9)

```
[new] backend/app/models/club.py
[mod] backend/app/models/__init__.py (+ Club, ClubMember)
[new] backend/alembic/versions/006_create_clubs.py
[new] backend/app/schemas/club.py
[new] backend/app/api/v1/clubs.py
[mod] backend/app/api/v1/router.py (+ clubs_router)
[new] backend/app/tests/test_clubs.py (23 tests)
[new] frontend/src/api/clubs.ts
[new] frontend/src/pages/ClubsPage.tsx
[new] frontend/src/pages/ClubPage.tsx
[mod] frontend/src/App.tsx (+ /clubs, /clubs/:slug)
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
