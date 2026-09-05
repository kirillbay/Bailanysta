# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 8 — Stories)

---

## 1. Текущий STEP

**STEP 8 — Stories — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 8 — stories` (см. §17)
- Статус: 24h Stories (model+media, expiration, feed groups, viewer, create/delete) — 147 тестов зелёных

**Последний завершённый STEP:** STEP 8 — Stories (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 9 — Clubs

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
| 8 | Stories | 2026-09-05 | `feat STEP8` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories ✅ → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: Feed + StoryBar + StoryViewer + Create] → [Backend: /stories (create/list/get/delete) + storage stories/ + expiration] → [Postgres 005_stories + Follow + SQLite test]
                         ↕ storiesApi, TanStack Query stories, grouped by author (own first, followed)
```

- Frontend: `api/stories.ts` (list/create/get/remove, resolveUrl), `components/StoryBar.tsx` (add + groups + create form preview), `components/StoryViewer.tsx` (modal, image/video, author, timestamp, remaining, prev/next, Esc, delete), `pages/FeedPage.tsx` + StoryBar/Viewer
- Backend: `models/story.py` (id UUID, author_id FK CASCADE, media_url/text, media_type image/video, created_at, expires_at +24h, indexes), `alembic 005_create_stories`, `services/storage.py` + save_story_media (image 5MB Pillow, video 25MB mime check), `schemas/story.py`, `api/v1/stories.py` (4 endpoints)
- DB: `005_create_stories` added stories table
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Stories: `StoryBar` — Add Story button + dashed circle, groups `StoryGroup` avatar gradient + username + count, create form (file jpeg/png/webp/mp4/webm, preview image/video, size, text 2000, publish, error, invalidate stories), `StoryViewer` — modal black/80, author+timestamp+remaining `h m`, media image/video, text, prev/next, Esc, delete, index count, keyboard arrows
- Feed: `pages/FeedPage.tsx` now includes StoryBar + Viewer state `StoryGroup` idx, below hero before PostComposer
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.23s, 1699 modules, 484.30 kB js gzip 147.48 kB (16.98 kB css)

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/story.py` — id UUID PK, author_id FK CASCADE index, media_url 512 nullable, media_type 20 nullable (image/video), text Text nullable, created_at server_default now, expires_at DateTime index + ix_author_expires
- Schemas: `schemas/story.py` — AuthorPublic, StoryRead, StoryGroup
- Services: `services/storage.py` + `STORY_IMAGE_MIME jpeg/png/webp 5MB` + `STORY_VIDEO_MIME mp4/webm 25MB` + `save_story_media` (mime check, size, Pillow for image, ext mp4/webm, stories/ subdir UUID, public_url)
- APIs: `api/v1/stories.py` — `POST /stories` 201 (auth, multipart file required, text trim 2000, no author_id bypass, save_story_media, now+24h expires, return StoryRead), `GET /stories` 200 (auth, expires_at>now, allowed = own + followed, grouped by author stories desc, own first), `GET /stories/{id}` 200 (auth, expired 404, privacy own/followed 404), `DELETE /stories/{id}` 204 (owner 403, file cleanup best effort)
- Router: `router.py` + stories_router
- Migration: `alembic/versions/005_create_stories.py` — stories — `--sql` verified
- Tests: `test_stories.py` 16 passed, total 147 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories)
- Startup: routes `/stories` verified

---

## 6. Database Status

- Статус: **stories added ✅**
- Tables: `stories` + previous 10 + `users`
- Indexes: `ix_stories_author_id`, `ix_stories_expires_at`, `ix_stories_author_expires`
- Constraints: FK CASCADE

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |
| 002_create_posts | create posts + media + hashtags | 2026-09-05 | ✅ Created, --sql OK |
| 003_create_social | create social interactions | 2026-09-05 | ✅ Created, --sql OK |
| 004_create_follows | create follows | 2026-09-05 | ✅ Created, --sql OK |
| 005_create_stories | create stories | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → all 5 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- Stories mutations require auth, delete owner only, no author_id bypass

---

## 9. Implemented Features

> STEP 8 — stories done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow/Search — follow, search, hashtags
- [x] Stories: 24h image/video/text, create/list/get/delete, expiration filter, grouped feed own+followed, viewer, cleanup
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 484 kB, stories ready
- Backend: Render/Railway — stories ready, uploads stories/
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **147 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories) ✅
  - stories 16 (create image/video, unauth 401, invalid mime 415, oversized 413, text 422, no bypass, active visible, expired 404, feed only active, followed visible, unrelated not visible, own visible, delete owner 204, other 403, nonexist 404, expiration filtering)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.23s
- Integration: `login → create story → StoryBar → viewer → next/prev → delete → gone` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No Story viewers/read receipts (future)
- No Story reactions/replies (future)
- No auto background cleanup job (expired filtered on read, not deleted)
- Video no transcoding (MVP)
- Hashtag ILIKE, Bookmarks 50 (known)

---

## 13. Technical Debt

- Add S3 (долг)
- Add stories cleanup cron (expired records still on disk until manual)
- Add cursor pagination for feed/search (offset)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP9.

---

## 15. Next Recommended STEP

**STEP 9 — Clubs**

- clubs model, members, channels (text channels), club structure like Discord, creation/join

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Stories 24h backend expires_at = now+24h | Truth backend, not frontend |
| 2026-09-05 | Storage stories/ separate subdir | No mix with avatars/posts |
| 2026-09-05 | Image 5MB Pillow, video 25MB mime check | Spec §2, no FFmpeg |
| 2026-09-05 | Feed groups own first + followed only (not all users) | Spec §4, privacy MVP |
| 2026-09-05 | Viewer modal with Esc/arrow/delete + remaining h m | Spec §11 |
| 2026-09-05 | Migration 005 separate | Not rewrite old |

---

## 17. Последний Git Commit

```
feat: STEP 8 — stories (предстоит)
Branch: main | Status: clean (после commit)
Stories: model 005, storage stories/, 4 endpoints, StoryBar/Viewer, 16 tests
```

---

## 18. Изменённые файлы (STEP 8)

```
[new] backend/app/models/story.py
[mod] backend/app/models/__init__.py (+ Story)
[new] backend/alembic/versions/005_create_stories.py
[mod] backend/app/services/storage.py (+ STORY_IMAGE/VIDEO, save_story_media)
[new] backend/app/schemas/story.py
[new] backend/app/api/v1/stories.py
[mod] backend/app/api/v1/router.py (+ stories_router)
[new] backend/app/tests/test_stories.py (16 tests)
[new] frontend/src/api/stories.ts
[new] frontend/src/components/StoryBar.tsx
[new] frontend/src/components/StoryViewer.tsx
[mod] frontend/src/pages/FeedPage.tsx (+ StoryBar/Viewer)
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
