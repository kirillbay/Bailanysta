# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 6 — Feed & Social Interactions)

---

## 1. Текущий STEP

**STEP 6 — Feed & Social Interactions — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 6 — feed and social interactions` (см. §17)
- Статус: глобальный feed + likes/comments/reposts/bookmarks + PostCard интеракции + BookmarksPage — 110 тестов зелёных

**Последний завершённый STEP:** STEP 6 — Feed & Social Interactions (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 7 — Follow / Search / Hashtags

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
| 6 | Feed & Social Interactions | 2026-09-05 | `feat STEP6` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: Feed global + PostCard (like/comment/repost/bookmark) + Bookmarks + PostDetail comments] → [Backend: /feed + /posts/{id}/like|repost|bookmark + /comments + /bookmarks + posts enriched] → [Postgres 003_social + SQLite test]
                         ↕ optimistic UI (like/repost/bookmark), TanStack Query feed/post/bookmarks/comments
```

- Frontend: `api/feed.ts`, `api/comments.ts`, `api/bookmarks.ts`, `api/posts.ts` + counts, `components/PostCard.tsx` interaction bar + CommentSection, `pages/FeedPage.tsx` global feed + load more, `pages/PostDetailPage.tsx` withComments, `pages/BookmarksPage.tsx`, `App.tsx` /bookmarks
- Backend: `models/social.py` (PostLike, Comment, PostRepost, Bookmark), `alembic 003_create_social`, `schemas/comment.py`, `schemas/post.py` + counts, `api/v1/feed.py` + `comments.py` + `bookmarks.py` + `posts.py` enriched (+likes/reposts/bookmarks endpoints), `users.py` enriched
- DB: `003_create_social` added 4 tables + indexes + unique
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Feed: `pages/FeedPage.tsx` — global `feedApi.get(limit, offset)` with offset state, `allPosts` accumulation, skeleton/empty/error, load more, composer invalidate feed
- PostCard: `PostCard.tsx` — author, hashtags, media, interaction bar (Heart likes_count/red, MessageCircle comments_count, Repeat2 reposts_count green, Bookmark blue, Share2 copy link), optimistic toggle like/repost/bookmark with rollback + invalidate feed/bookmarks, edit/delete owner, withComments toggle, CommentSection (list, create, edit/delete own, author, timestamp)
- APIs: `api/posts.ts` + like/unlike/repost/unrepost/bookmark/unbookmark, `api/feed.ts`, `api/comments.ts`, `api/bookmarks.ts`
- Bookmarks: `pages/BookmarksPage.tsx` — query bookmarks, empty state, PostCard, refetch on update
- Detail: `pages/PostDetailPage.tsx` — query post, withComments true
- Routing: `App.tsx` `/bookmarks` protected, `/posts/:postId`, `/` feed protected
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.61s, 1692 modules, 469.60 kB js gzip 144.19 kB (16.45 kB css)

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/social.py` — `PostLike`/`PostRepost`/`Bookmark` (UUID PK, post_id FK CASCADE, user_id FK CASCADE, created_at, Unique post+user, indexes), `Comment` (UUID PK, post_id FK CASCADE index, author_id FK CASCADE index, content Text, created/updated, author joined, ix_comments_post_created)
- Schemas: `schemas/comment.py` (AuthorPublic, CommentRead, Create 1-2000, Update 1-2000), `schemas/post.py` + counts/liked/reposted/bookmarked
- Migration: `alembic/versions/003_create_social.py` — post_likes, comments, post_reposts, bookmarks — `--sql` verified
- API: `api/v1/posts.py` enriched `_enrich_many` (bulk counts via func.count group_by + liked/reposted/bookmarked sets), `_get_current_user_optional`, `GET /posts/{id}` public optional auth, `GET /posts/by/user` enriched, `PATCH/DELETE` enriched, `POST/DELETE /posts/{id}/like|repost|bookmark` (auth, 404, idempotent Already liked/detail, 204 on unlike, counts via DB), `api/v1/feed.py` `GET /feed` auth created_at DESC pagination limit 50 offset, `_enrich`, `api/v1/comments.py` `GET /posts/{id}/comments` public 404, `POST /posts/{id}/comments` auth 201, `PATCH /comments/{id}` owner 403, `DELETE` owner 403, content 1-2000, `api/v1/bookmarks.py` `GET /bookmarks` auth user_created desc, enrich, `api/v1/users.py` `GET /users/{username}/posts` enriched counts, `router.py` includes feed/comments/bookmarks
- Tests: `test_social.py` 24 passed, total 110 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social)
- Startup: routes `/feed`, `/posts/{id}/like`, `/comments` etc verified

---

## 6. Database Status

- Статус: **social added ✅**
- Tables: `post_likes`, `comments`, `post_reposts`, `bookmarks` + previous 5 + `users`
- Indexes: `ix_post_likes_post_user`, `ix_comments_post_created`, `ix_post_reposts_post_user`, `ix_bookmarks_post_user`, `ix_bookmarks_user_created` etc
- Constraints: Unique post+user for like/repost/bookmark, FK CASCADE

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |
| 002_create_posts | create posts + media + hashtags | 2026-09-05 | ✅ Created, --sql OK |
| 003_create_social | create social interactions | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → all 3 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- All social mutations require `get_current_user` — 401 if missing, IDOR checks for comment edit/delete (author_id), likes/bookmarks isolated per user

---

## 9. Implemented Features

> STEP 6 — feed/social done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover
- [x] Posts — create, user posts, patch/delete
- [x] Feed: global feed `GET /feed` created_at DESC paginated + PostCard integration
- [x] Social: likes (duplicate idempotent, unlike, counts, liked_by_me), comments (create/read/update/delete own, pagination), reposts (counts, reposted_by_me), bookmarks (create/remove, GET /bookmarks isolation)
- [ ] Follow/Search — STEP7
- [ ] Stories — STEP8
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 469 kB, feed ready
- Backend: Render/Railway — feed/social ready
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **110 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social) ✅
  - feed 4 (auth, pagination, empty, requires auth), likes 5 (like/unlike, dup, unauth, nonexist, isolation), comments 8 (create/read, update own, delete own, cannot update other 403, empty 422, too long 422, unauth 401, nonexist 404), reposts 3 (repost/unrepost, dup, unauth 401), bookmarks 4 (bookmark/remove + feed flags, dup, isolation, unauth)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.61s
- Integration: `login → create post → global feed → like → unlike → comment → edit → delete → bookmark → /bookmarks → repost` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No markdown rendering (XSS safe text)
- No nested comment replies (flat MVP)
- No follow system (STEP7)
- Hashtag search not yet (STEP7)
- Bookmarks page no pagination load more (limit 50, simple)
- Feed is global chronological, no personalization (future)

---

## 13. Technical Debt

- Add S3 (долг)
- Add image resize (долг)
- Add cursor pagination for feed (currently offset)
- Add pagination for comments `load more` (currently 20 fixed)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP7.

---

## 15. Next Recommended STEP

**STEP 7 — Follow / Search / Hashtags**

- Follow model, search endpoint (users/posts/hashtags), hashtag search using existing tables

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Feed `created_at DESC` limit 50 offset, bulk counts via group_by | MVP simple, spec §1, no N+1 |
| 2026-09-05 | Likes/Reposts/Bookmarks Unique post+user + idempotent Already liked | Spec §2/4/5 |
| 2026-09-05 | Comments flat, 1-2000 Text, no nested | Spec §3 MVP |
| 2026-09-05 | PostRead enriched with counts + liked/bookmarked/reposted flags | Spec §6 no N+1 |
| 2026-09-05 | Optimistic UI like/repost/bookmark with rollback + invalidate feed/bookmarks | Spec §2/9 UX |
| 2026-09-05 | Migration 003 separate | Not rewrite old migrations |

---

## 17. Последний Git Commit

```
feat: STEP 6 — feed and social interactions (предстоит)
Branch: main | Status: clean (после commit)
Feed/social: 003 migration, models, 7 endpoints, PostCard interactions, Feed/Bookmarks, 24 tests
```

---

## 18. Изменённые файлы (STEP 6)

```
[new] backend/app/models/social.py
[mod] backend/app/models/__init__.py (+ social)
[new] backend/alembic/versions/003_create_social.py
[mod] backend/app/schemas/post.py (+ counts)
[new] backend/app/schemas/comment.py
[mod] backend/app/api/v1/posts.py (enriched + like/repost/bookmark)
[new] backend/app/api/v1/feed.py
[new] backend/app/api/v1/comments.py
[new] backend/app/api/v1/bookmarks.py
[mod] backend/app/api/v1/users.py (enriched)
[mod] backend/app/api/v1/router.py (+ feed/comments/bookmarks)
[new] backend/app/tests/test_social.py (24 tests)
[mod] frontend/src/api/posts.ts (+ like/repost/bookmark)
[new] frontend/src/api/feed.ts
[new] frontend/src/api/comments.ts
[new] frontend/src/api/bookmarks.ts
[mod] frontend/src/components/PostCard.tsx (interaction bar + comments + optimistic)
[new] frontend/src/pages/BookmarksPage.tsx
[mod] frontend/src/pages/FeedPage.tsx (global feed)
[mod] frontend/src/pages/PostDetailPage.tsx (withComments)
[mod] frontend/src/App.tsx (+ /bookmarks)
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
