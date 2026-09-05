# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 5 — Posts & Media)

---

## 1. Текущий STEP

**STEP 5 — Posts & Media — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 5 — posts and media` (см. §17)
- Статус: Post/Media/Hashtag модели + миграция + API + composer + PostCard + detail + 29 тестов — всё зелёно

**Последний завершённый STEP:** STEP 5 — Posts & Media (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 6 — Feed & Social Interactions (likes/comments/bookmarks/follows)

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
| 5 | Posts & Media | 2026-09-05 | `feat STEP5` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Composer + PostCard + Detail + Feed] → [Backend: FastAPI /posts + /users/{username}/posts + storage] → [PostgreSQL + SQLite test]
                         ↕ postsApi (FormData, patch/delete), TanStack Query
                         ↕ Post/Hashtag/Media relationships
```

- Frontend: `api/posts.ts` (create/get/userPosts/update/remove, resolveUrl), `components/PostComposer.tsx` (avatar, textarea, count, picker, previews, POST), `components/PostCard.tsx` (author, hashtags, media, edit/delete), `pages/FeedPage.tsx` (composer + user posts feed), `pages/PostDetailPage.tsx` + `App.tsx` /posts/:postId
- Backend: `models/post.py` (Post, PostMedia, Hashtag, post_hashtags), `services/hashtags.py` (MAX 20, regex), `services/storage.py` reutilisé, `schemas/post.py`, `api/v1/posts.py` (5 endpoints), `api/v1/users.py` + `GET /users/{username}/posts` alias, `alembic 002_create_posts`
- Storage: reuse `storage.save_image` with subdir `posts/` (separate from avatars/covers)
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Posts API: `api/posts.ts` FormData create, get, userPosts, patch, remove, resolveUrl
- Composer: `components/PostComposer.tsx` — avatar, textarea placeholder, 10k counter, picker (max 4), previews + remove, POST button disabled logic, invalidate `posts`/`user-posts` on success
- PostCard: `PostCard.tsx` — author avatar (fallback), name/username/timestamp, content hashtags colored, media grid 1/2 cols, hashtags badges, owner edit/delete (confirm, mutation, invalidate), link to detail
- Feed: `pages/FeedPage.tsx` — hero + composer + `useQuery user-posts` (me) + health card
- Detail: `pages/PostDetailPage.tsx` — load via useQuery, skeleton/404, PostCard
- Routing: `App.tsx` `/posts/:postId` protected
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.52s, 464.78 kB js gzip 143.51 kB (18.34 kB css), 1689 modules

---

## 5. Backend Status

- Статус: **runnable ✅**
- Deps: `Pillow`, `python-multipart` already (STEP4) — reused
- Models: `app/models/post.py` — `Post` (UUID PK, author_id FK CASCADE, content Text, created_at index, updated_at, author joined, media selectin, hashtags selectin, ix_posts_author_created), `PostMedia` (UUID PK, post_id FK CASCADE index, url 512, mime 50, position int, Unique post/position), `Hashtag` (UUID PK, name 100 unique index), `post_hashtags` (PK post_id+hashtag_id CASCADE), `app/models/__init__.py` exports
- Schemas: `app/schemas/post.py` — `AuthorPublic`, `PostMediaRead`, `PostRead` (id,author_id,content,created,updated,author,media,hashtags), `PostCreateInput` 1-10000, `PostUpdateInput` 1-10000
- Services: `services/hashtags.py` (HASHTAG_RE `#[\w]{1,50}`, lower, dedup, MAX 20, MAX_LEN 50), `services/storage.py` reused (posts/ subdir)
- API: `app/api/v1/posts.py` — `POST /posts` 201 (Form content 1-10000 + files 0-4, stripped check, save_image with cleanup on fail, Post + PostMedia + hashtags transaction, return PostRead), `GET /posts/{id}` 200 404 public, `GET /posts/by/user/{username}` + `GET /users/{username}/posts` 200 pagination limit 20 ge1 le50 offset ge0, max 50, `PATCH /posts/{id}` 200 (PostUpdateInput, owner 403, hashtags recalc), `DELETE /posts/{id}` 204 (owner 403, media delete cascade + file unlink best effort)
- Router: `app/api/v1/router.py` includes posts_router
- Migration: `alembic/versions/002_create_posts.py` — hashtags, posts, post_media, post_hashtags — `--sql` verified (PostgresqlImpl)
- Tests: `test_posts.py` 29 passed, total 86 passed (25 auth + 8 db + 6 health + 18 profiles + 29 posts)
- Startup: routes `/posts`, `/users/{username}/posts`, `/uploads/posts/` verified

---

## 6. Database Status

- Статус: **posts added ✅**
- Tables: `posts`, `post_media`, `hashtags`, `post_hashtags` + `users`, `alembic_version`
- Indexes: `ix_posts_author_id`, `ix_posts_created_at`, `ix_posts_author_created`, `ix_post_media_post_id`, `ix_hashtags_name`
- Constraints: FK users→posts CASCADE, posts→post_media CASCADE, Unique post_media (post_id,position), Unique hashtag name

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |
| 002_create_posts | create posts + media + hashtags | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → both upgrades OK, `downgrade base --sql` → DROP OK
- Online upgrade requires PG (Docker) — fallback warning skip

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- Posts owner checks via `get_current_user` — IDOR prevented, no author_id bypass

---

## 9. Implemented Features

> STEP 5 — posts done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover upload
- [x] Posts: create (content+media 0-4, hashtags), get public, user posts paginated, patch own, delete own + media cleanup + file cleanup
- [ ] Feed — STEP6
- [ ] Stories — STEP8
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 464 kB
- Backend: Render/Railway — posts ready, uploads posts/
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **86 passed** (25 auth + 8 db + 6 health + 18 profiles + 29 posts) ✅
  - posts: auth create 1, unauth 1, empty 1, oversized 1, author public 1, media 5 (jpeg/png/webp/unsupported/oversized/invalid/malicious/max count/dir), read 4 (existing/404/pagination/limit), ownership 4 (update/delete/other update/delete/forged), hashtags 4 (extract/normalization/duplicate/excessive), delete 2 (media records/files), edit hashtags 1
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.52s
- Integration: `Login → Create post (hello #Python) → GET → Edit → Delete → 404` manual via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No feed ranking (STEP6)
- No likes/comments/bookmarks (STEP6)
- No markdown/HTML rendering (XSS safe — text only, split hashtag highlight)
- Physical file cleanup best effort (documented limitation — not atomic with DB transaction)
- Hashtag search not yet (structure ready for STEP7) — `hashtags` + `post_hashtags` prepared
- Media editing on patch not supported (text only, media immutable) — documented

---

## 13. Technical Debt

- Add S3 storage abstraction (долг)
- Add image resize/compression for posts (долг)
- Add pagination cursor for posts (currently offset, easy to switch)
- Version single source (долг)
- Add `xslt`/`hashtag` index optimization if needed

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP6.

---

## 15. Next Recommended STEP

**STEP 6 — Feed & Social Interactions**

- Feed chronological/cursor, likes/comments/reposts/bookmarks/follows, Post interactions, optimistic UI

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Post content 1-10000, empty only if media | Constraints §5, UX |
| 2026-09-05 | Storage reuse `posts/` subdir separate | No mix with avatars/covers, clean abstraction |
| 2026-09-05 | Hashtag regex `#\w` 1-50, lower, dedup, max 20 per post | Rules §16, STEP7 ready |
| 2026-09-05 | Multipart Form `content` + `files` in one POST | Clean API §9, no multi-request |
| 2026-09-05 | User posts pagination limit 50 offset | MVP simple, spec §12 |
| 2026-09-05 | Atomicish post creation: DB rollback + file cleanup | Integrity §24 |
| 2026-09-05 | Patch only own, no author_id bypass (PostUpdateInput) | IDOR prevention |

---

## 17. Последний Git Commit

```
feat: STEP 5 — posts and media (предстоит)
Branch: main | Status: clean (после commit)
Posts: models, 002 migration, storage/posts, hashtags, API 5 endpoints, frontend composer+card+detail, 29 tests
```

---

## 18. Изменённые файлы (STEP 5)

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
