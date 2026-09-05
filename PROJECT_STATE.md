# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 7 — Follow, Search & Hashtags)

---

## 1. Текущий STEP

**STEP 7 — Follow, Search & Hashtags — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 7 — follow search and hashtags` (см. §17)
- Статус: Follow + Search (users/posts/hashtags) + HashtagPage + Profile follow + 21 тест — 131 passed

**Последний завершённый STEP:** STEP 7 — Follow, Search & Hashtags (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 8 — Stories

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
| 7 | Follow, Search & Hashtags | 2026-09-05 | `feat STEP7` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: Profile follow + Search tabs + HashtagPage → API search] → [Backend: /users/{username}/follow|followers|following + /search + /hashtags/{name} + enriched profile] → [Postgres 004_follows + SQLite test]
                         ↕ optimistic follow, debounce 400ms, hashtag links
```

- Frontend: `api/follows.ts`, `api/search.ts` (users/posts/hashtags), `pages/ProfilePage.tsx` + follow button + counts + optimistic, `pages/SearchPage.tsx` (tabs All/Users/Posts/Hashtags, debounce 400ms), `pages/HashtagPage.tsx`, `components/PostCard.tsx` hashtag links, `App.tsx` /search + /hashtags/:name
- Backend: `models/follow.py` (id UUID, follower/following FK CASCADE, Unique, indexes), `alembic 004_create_follows`, `api/v1/follows.py` (4 endpoints), `api/v1/search.py` unified `GET /search?q&type&limit&offset` (users ILIKE, posts ILIKE, hashtags ILIKE, no secrets, limit 50, trim), `api/v1/hashtags.py` (GET /hashtags/{name} + /posts), `api/v1/users.py` enriched `GET /users/{username}` with followers/following/is_following
- DB: `004_create_follows` added follows table
- Детали → `ARCHITECTURE.md`, `SECURITY.md`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Follow: `pages/ProfilePage.tsx` — followers/following counts, Follow/Following button optimistic with `followsApi.follow/unfollow`, invalidation profile, own vs other logic
- Search: `pages/SearchPage.tsx` — input `q` with debounce 400ms `useDebounce`, tabs All/Users/Posts/Hashtags, sections users (avatar+username+followers), posts (PostCard), hashtags (card), loading/error/empty/no query, search via `searchApi.search`
- Hashtag: `pages/HashtagPage.tsx` — `useParams name`, `searchApi.hashtag` + `hashtagPosts` with offset load more, PostCard, 404, skeleton, empty
- PostCard: hashtags clickable `Link /hashtags/:name`, content split links
- Routing: `App.tsx` `/search` → SearchPage, `/hashtags/:name` → HashtagPage, `/profile/:username` still, `/bookmarks` etc
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.09s, 1696 modules, 477.54 kB js gzip 146.04 kB (16.54 kB css)

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/follow.py` — id UUID PK, follower_id FK CASCADE index, following_id FK CASCADE index, created_at, Unique follower+following, indexes follower_following, following_follower
- Schemas: `schemas/user.py` unchanged (public profile now returns dict with followers/following/is_following, not strict UserPublic model but compatible)
- Migration: `alembic/versions/004_create_follows.py` — follows — `--sql` verified
- APIs: `api/v1/follows.py` — `POST /users/{username}/follow` 201 (auth, 404, 400 self, idempotent), `DELETE` 204 idempotent, `GET /followers` + `GET /following` paginated limit 50 offset, items with followers/following counts, total; `api/v1/search.py` unified, `GET /search?q&type&limit&offset` (trim, max 100, 422 if >100, empty → empty lists, ILIKE lower for users display_name/username, posts content, hashtags name, bulk counts for posts, no email/hash leak), `api/v1/hashtags.py` `GET /hashtags/{name}` 404, `GET /posts` paginated, case-insensitive lower, `api/v1/users.py` enriched `GET /users/{username}` with followers/following/is_following via cookie decode optional
- Router: `router.py` includes follows/search/hashtags
- Tests: `test_follow_search.py` 21 passed, total 131 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search)
- Startup: routes `/users/{username}/follow`, `/search`, `/hashtags/{name}` verified

---

## 6. Database Status

- Статус: **follows added ✅**
- Tables: `follows` + previous 9 + `users`
- Indexes: `ix_follows_follower_id`, `ix_follows_following_id`, `ix_follows_follower_following`, `ix_follows_following_follower`
- Constraints: Unique follower+following, FK CASCADE

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |
| 002_create_posts | create posts + media + hashtags | 2026-09-05 | ✅ Created, --sql OK |
| 003_create_social | create social interactions | 2026-09-05 | ✅ Created, --sql OK |
| 004_create_follows | create follows | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → all 4 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- Follow mutations require auth, self-follow blocked, idempotent, isolation per user

---

## 9. Implemented Features

> STEP 7 — follow/search done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow button + counts
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow: follow/unfollow, followers/following lists paginated, counts, is_following, optimistic
- [x] Search: users (username/display_name ILIKE), posts (content/hashtag ILIKE), hashtags (name ILIKE), unified `GET /search`, pagination, no secrets
- [x] Hashtags: `GET /hashtags/{name}` case-insensitive, `GET /hashtags/{name}/posts` paginated, HashtagPage, click from PostCard
- [ ] Stories — STEP8
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 477 kB, search/hashtags ready
- Backend: Render/Railway — follow/search ready
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **131 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search) ✅
  - follow 8 (follow/unfollow, dup, self 400, unauth 401, nonexist 404, followers/following lists, pagination 2+2, isolation), search 5+3 (users by username/display_name case-insensitive, pagination empty, too long 422, no sensitive, posts by content/hashtag case-insensitive), hashtags 4 (existing, case norm 3 variants, posts, nonexist 404)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.09s
- Integration: `register → follow → counts → unfollow → followers list → search user/post/hashtag → hashtag page → post` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No Stories/Clubs/Messages (future)
- Hashtag search is ILIKE, not full-text (MVP)
- Bookmarks pagination simple (50)
- Feed global chronological, no following feed personalization (debt)
- Search no type=all sections limit fixed 10 (MVP)

---

## 13. Technical Debt

- Add S3 (долг)
- Add cursor pagination for feed/search (currently offset)
- Add Elasticsearch/OpenSearch later if needed (currently PG ILIKE)
- Add following feed personalization (STEP7 debt, documented)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP8.

---

## 15. Next Recommended STEP

**STEP 8 — Stories**

- stories model (image/video/text, expires 24h), create/view/delete, frontend stories bar

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Follow id UUID + Unique follower+following + self check | Spec §1, security |
| 2026-09-05 | Search unified `GET /search?q&type` with ILIKE lower | Simple, spec §4-6, no ES |
| 2026-09-05 | Search users ILIKE username/display_name, no email/hash | Privacy §5 |
| 2026-09-05 | Hashtag case-insensitive via lower (already lower normalized) | Spec §7, STEP5 lower |
| 2026-09-05 | HashtagPage + clickable PostCard hashtags | Spec §8, UX |
| 2026-09-05 | Profile follow optimistic + counts invalidate | Spec §3 UX |
| 2026-09-05 | Migration 004 separate | Not rewrite old |

---

## 17. Последний Git Commit

```
feat: STEP 7 — follow search and hashtags (предстоит)
Branch: main | Status: clean (после commit)
Follow/search: 004 migration, follow model, 4 follow endpoints, search, hashtags, Profile follow, Search/Hashtag pages, 21 tests
```

---

## 18. Изменённые файлы (STEP 7)

```
[new] backend/app/models/follow.py
[mod] backend/app/models/__init__.py (+ Follow)
[new] backend/alembic/versions/004_create_follows.py
[new] backend/app/api/v1/follows.py
[new] backend/app/api/v1/search.py
[new] backend/app/api/v1/hashtags.py
[mod] backend/app/api/v1/users.py (enriched profile with counts/is_following)
[mod] backend/app/api/v1/router.py (+ follows/search/hashtags)
[new] backend/app/tests/test_follow_search.py (21 tests)
[new] frontend/src/api/follows.ts
[new] frontend/src/api/search.ts
[mod] frontend/src/pages/ProfilePage.tsx (follow button + counts)
[new] frontend/src/pages/SearchPage.tsx
[new] frontend/src/pages/HashtagPage.tsx
[mod] frontend/src/components/PostCard.tsx (hashtag links)
[mod] frontend/src/App.tsx (+ /search, /hashtags/:name)
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
