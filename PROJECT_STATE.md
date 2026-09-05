# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 10 — Club Channels & Messaging)

---

## 1. Текущий STEP

**STEP 10 — Club Channels & Messaging — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 10 — club channels and messaging` (см. §17)
- Статус: ClubChannel + ClubMessage (CRUD + pagination + IDOR) + ClubChannelPage + 15 тестов — 185 passed, build зеленый, realtime отложен на STEP11

**Последний завершённый STEP:** STEP 10 — Club Channels & Messaging (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 11 — Notifications & Realtime (WebSocket, notifications)

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
| 10 | Club Channels & Messaging | 2026-09-05 | `feat STEP10` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories ✅ → 9 Clubs ✅ → 10 Channels/Messaging ✅ → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: Clubs + ClubPage(Channels) + ClubChannelPage(Messages) + Feed/Stories] → [Backend: /clubs/{slug}/channels + /clubs/{slug}/channels/{cslug}/messages + clubs] → [Postgres 007_club_channels_messages + SQLite test]
                         ↕ clubChannelsApi, TanStack Query channels/messages
                         ↕ Club → ClubChannel → ClubMessage (CASCADE)
```

- Frontend: `api/clubChannels.ts` (list/get/create/update/remove + messages/send/edit/remove), `pages/ClubPage.tsx` + ChannelsSection (list, create, edit/delete), `pages/ClubChannelPage.tsx` (sidebar channels + messages + composer), `App.tsx` /clubs/:slug/channels/:channelSlug
- Backend: `models/club_channel.py` (ClubChannel), `models/club_message.py` (ClubMessage), `alembic 007_create_club_channels_messages`, `schemas/club_channel.py`, `api/v1/club_channels.py` (5 channels endpoints), `api/v1/club_messages.py` (4 messages endpoints), `services/storage.py` unchanged (no attachments)
- DB: `007_create_club_channels_messages` added club_channels + club_messages
- Детали → `ARCHITECTURE.md` (Club → Channels → Messages), `SECURITY.md` (channel/message IDOR)

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Clubs: `ClubsPage.tsx` unchanged, `ClubPage.tsx` now `ChannelsSection` (list channels, create owner/admin, edit/delete)
- Channels: `ClubChannelPage.tsx` — двухколоночный layout `grid lg:240px 1fr`, sidebar channels list (active highlight), main messages (avatar, author, timestamp, edited, content, edit/delete), pagination `Load older`, composer textarea Enter=send Shift+Enter newline, max 10000, trim, disable empty, invalidate messages
- APIs: `api/clubChannels.ts` all 9 functions
- Routing: `App.tsx` `/clubs/:slug/channels/:channelSlug` protected
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.45s, 1704 modules, 504.01 kB js gzip 150.94 kB (17.29 kB css) — chunks >500kB warning (code-split debt)

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/club_channel.py` — id UUID PK, club_id FK CASCADE index, name 100, slug 100, description Text, position int, created/updated, Unique club+slug, index club+position; `models/club_message.py` — id UUID PK, channel_id FK CASCADE index, author_id FK CASCADE index, content Text, is_edited bool false, created/updated, author joined, index channel+created
- Schemas: `schemas/club_channel.py` — ChannelCreate 1-100 + desc 500, ChannelUpdate, ChannelRead, AuthorPublic, MessageCreate/Update 1-10000, MessageRead
- Migration: `alembic/versions/007_create_club_channels_messages.py` — club_channels + club_messages — `--sql` verified (upgrade/downgrade)
- APIs: `api/v1/club_channels.py` — `GET /clubs/{slug}/channels` member 403, ordered position+created, `GET /{channel_slug}` member, 404 cross-club, `POST` owner/admin 403 member/moderator, slugify unique, position auto max+1, `PATCH` owner/admin, `DELETE` owner/admin CASCADE; `api/v1/club_messages.py` — `GET /messages` member 403, limit 50 le100 offset, ordered asc, `POST` member 403, content trim 1-10000, author current_user, `PATCH` owner only 403 other, `DELETE` author or owner/admin/moderator can delete other, member cannot delete other, IDOR via channel→club check, forged channel/message 404
- Router: `router.py` + channels + club_messages
- Tests: `test_club_channels.py` 15 passed, total 185 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels)
- Startup: routes `/clubs/{slug}/channels`, `/.../messages` verified

---

## 6. Database Status

- Статус: **channels/messages added ✅**
- Tables: `club_channels`, `club_messages` + previous 12 + `users`
- Indexes: `ix_club_channels_club_id`, `ix_channels_club_position`, `ix_club_messages_channel_id`, `ix_club_messages_author_id`, `ix_messages_channel_created`
- Constraints: Unique club+slug, FK CASCADE

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

- `alembic upgrade head --sql` → all 7 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- All channel/message mutations require member + role checks, no author_id bypass

---

## 9. Implemented Features

> STEP 10 — channels/messaging done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow/Search — follow, search, hashtags
- [x] Stories — 24h image/video/text, grouped feed, viewer
- [x] Clubs — create, list/search, detail, join/leave, members, roles, avatar/cover
- [x] Channels: create/list/get/update/delete (owner/admin), position auto, slug unique per club, member only access
- [x] Messages: send (member), list paginated 50 le100, edit own only, delete own or moderator/admin/owner, is_edited, ordered asc, no N+1, IDOR cross-club blocked
- [ ] Messaging private — future (not STEP10)
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 504 kB, channels/messaging ready
- Backend: Render/Railway — channels/messages ready
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **185 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels) ✅
  - channels 15 (create/list/get 1, permissions owner/admin 1, duplicate slug 1, update/delete 1, non-member 403 1, belongs correct 404 1, messages 9: send/list, empty/long 422, pagination, edit own, cannot edit other 403, delete own+moderator, non-member send 403, IDOR cross club 2, forged relationship 404)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.45s
- Integration: `register → create club → create channel → send message → edit → delete → cross-club blocked` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No realtime/WebSocket (STEP11) — HTTP polling only, no presence/typing
- No voice/video channels (future)
- No private messages (future)
- No attachments in messages (future)
- No reactions/threads (future)
- Hashtag ILIKE, Bookmarks 50 (known)
- Frontend chunks >500kB warning (code-split debt)

---

## 13. Technical Debt

- Add S3 (долг)
- Add channels reorder drag-drop (currently position auto)
- Add cursor pagination for messages (currently offset 50 le100)
- Add WebSocket for realtime (STEP11)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP11.

---

## 15. Next Recommended STEP

**STEP 11 — Notifications & Realtime**

- WebSocket for messages/notifications, notifications model, polling fallback

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | ClubChannel slugify channel + Unique club+slug + position auto max+1 | Spec §2, no duplicate |
| 2026-09-05 | ClubMessage 1-10000 Text, is_edited, FK CASCADE, index channel+created | Spec §3, XSS safe text |
| 2026-09-05 | Channels: member 403, create/update/delete owner/admin only | Spec §5, backend checks |
| 2026-09-05 | Messages: member 403, edit own only 403 other, delete own or owner/admin/moderator | Spec §7, no escalation |
| 2026-09-05 | Cross-club IDOR via channel→club check, forged 404 | Spec §8, security |
| 2026-09-05 | Messages ordered asc, pagination limit 50 le100, author joined no N+1 | Spec §7/20 performance |
| 2026-09-05 | Frontend ChannelPage grid 240px+1fr responsive, composer Enter/Shift+Enter | Spec §12/15 UX |
| 2026-09-05 | Migration 007 separate | Not rewrite old |
| 2026-09-05 | No WebSocket in STEP10 — HTTP foundation for STEP11 | Spec §23 |

---

## 17. Последний Git Commit

```
feat: STEP 10 — club channels and messaging (предстоит)
Branch: main | Status: clean (после commit)
Channels/Messaging: models 007, 5+4 endpoints, ClubChannelPage, 15 tests
```

---

## 18. Изменённые файлы (STEP 10)

```
[new] backend/app/models/club_channel.py
[new] backend/app/models/club_message.py
[mod] backend/app/models/__init__.py (+ ClubChannel, ClubMessage)
[new] backend/alembic/versions/007_create_club_channels_messages.py
[new] backend/app/schemas/club_channel.py
[new] backend/app/api/v1/club_channels.py
[new] backend/app/api/v1/club_messages.py
[mod] backend/app/api/v1/router.py (+ channels, club_messages)
[new] backend/app/tests/test_club_channels.py (15 tests)
[new] frontend/src/api/clubChannels.ts
[new] frontend/src/pages/ClubChannelPage.tsx
[mod] frontend/src/pages/ClubPage.tsx (+ ChannelsSection)
[mod] frontend/src/App.tsx (+ /clubs/:slug/channels/:channelSlug)
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
