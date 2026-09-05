# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 11 — Notifications & Realtime)

---

## 1. Текущий STEP

**STEP 11 — Notifications & Realtime — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 11 — notifications and realtime` (см. §17)
- Статус: Notification model+service+API + WebSocket manager + channel/message realtime + notifications UI/badge — 206 тестов зелёных, WebSocket работает, HTTP fallback сохранён, без Redis

**Последний завершённый STEP:** STEP 11 — Notifications & Realtime (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 12 — Projects

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
| 11 | Notifications & Realtime | 2026-09-05 | `feat STEP11` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles ✅ → 5 Posts ✅ → 6 Feed/Social ✅ → 7 Follow/Search ✅ → 8 Stories ✅ → 9 Clubs ✅ → 10 Channels/Messaging ✅ → 11 Notifications/Realtime ✅ → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
                    ┌───────────────┐
                    │    React      │  AppShell + Feed + ClubChannelPage + NotificationsPage
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
             PostgreSQL          Realtime Manager (in-memory, no Redis)
                 │                     │
           notifications           channel_subscribers + user_connections
```

```
Club
 ├── ClubMember
 ├── ClubChannel
 │    └── ClubMessage  (realtime broadcast)
User
 └── Notification (follow/like/comment)
```

- Frontend: `api/notifications.ts` (list/unread/markRead/markAll/remove), `api/stories.ts` etc, `hooks/useRealtime.ts` (useChannelRealtime, useNotificationsRealtime), `pages/NotificationsPage.tsx`, `pages/ClubChannelPage.tsx` + WS, `components/layout/AppShell.tsx` badge, `App.tsx` /notifications
- Backend: `models/notification.py` (id, recipient, actor, type, title/message, entity, is_read, created_at, indexes), `alembic 008_create_notifications`, `services/notifications.py` (create_notification, notify_follow/like/comment), `api/v1/notifications.py` (5 endpoints), `realtime/manager.py` (ConnectionManager), `api/v1/realtime.py` (WebSocket /ws, auth via cookie, subscribe with membership check, broadcast)
- Realtime: `manager.connect/disconnect/subscribe/broadcast_channel/send_to_user` (async Lock, user_connections, channel_subscribers)
- Events: `connected`, `subscribed`, `message.created|updated|deleted`, `notification.created`, `error`
- Детали → `ARCHITECTURE.md` (realtime diagram + event schema), `SECURITY.md` (WS auth, notifications IDOR)

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Notifications: `api/notifications.ts` + `pages/NotificationsPage.tsx` (list 50, unread badge, mark read/all, delete, actor avatar, title/message, entity link, timestamp, read/unread opacity), `AppShell.tsx` badge `unreadCount` via `useNotificationsRealtime` + `useQuery` cache, `99+` handling
- Realtime: `hooks/useRealtime.ts` (getWsUrl `VITE_API_URL` http→ws + `/api/v1/ws`, `useChannelRealtime` with backoff 1s→16s, `useNotificationsRealtime`), `pages/ClubChannelPage.tsx` + `useChannelRealtime(channelId)` + status badge `Connected/Reconnecting/Offline`, `StoryBar` etc still
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.23s, 1707 modules, 509.15 kB js gzip 152.05 kB (17.79 kB css) — chunks >500kB warning

---

## 5. Backend Status

- Статус: **runnable ✅**
- Models: `models/notification.py` — id UUID PK, recipient_id FK CASCADE index, actor_id FK SET NULL nullable, type 50, title 200 nullable, message Text nullable, entity_type 50 nullable, entity_id UUID nullable, is_read bool false, created_at, indexes recipient+created, recipient+is_read
- Schemas: `schemas/notification.py` implicit via dict, `services/notifications.py` ALLOWED_TYPES like/comment/follow/etc, `create_notification` (no self), `notify_follow/like/comment`
- Migration: `alembic/versions/008_create_notifications.py` — notifications — `--sql` verified
- APIs: `api/v1/notifications.py` — `GET /notifications?limit&offset&unread_only` 100 max new→old, `GET /unread-count` {count}, `PATCH /{id}/read` recipient only, `POST /read-all`, `DELETE /{id}` 204 recipient only; integration: `follows.py` POST follow → notify_follow + `await manager.send_to_user`, `posts.py` like → notify_like, `comments.py` comment → notify_comment, `club_messages.py` POST/PATCH/DELETE → `await manager.broadcast_channel` (ghost-free, DB commit before broadcast, dedup via message.id)
- Realtime: `realtime/manager.py` (user_connections, channel_subscribers, lock, connect/disconnect/subscribe/broadcast/send_to_user), `api/v1/realtime.py` (WebSocket /ws, auth via `decode_token` from cookie or `?token=` query, `user_id` from sub, `is_active`, close 4401, `subscribe` with `channel_id` UUID, verify `ClubChannel` exists + `ClubMember` membership, `unsubscribe`, `connected`/`subscribed`/`error`, max payload 10k, `manager` global)
- Router: `router.py` + notifications + realtime
- Tests: `test_notifications.py` 10 passed, `test_realtime.py` 11 passed, total 206 passed (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels + 21 realtime)
- Startup: routes `/notifications`, `/ws` verified

---

## 6. Database Status

- Статус: **notifications added ✅**
- Tables: `notifications` + previous 13 + `users`
- Indexes: `ix_notifications_recipient_id`, `ix_notifications_actor_id`, `ix_notifications_recipient_created`, `ix_notifications_recipient_read`
- Constraints: FK CASCADE (recipient), SET NULL (actor)

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

- `alembic upgrade head --sql` → all 8 upgrades OK
- Online requires PG

---

## 8. Authentication Status

- Статус: **unchanged ✅** (STEP3)
- WS auth via same `decode_token` (cookie `access_token` HttpOnly or `?token=`), `is_active`, `type==access`, close 4401, no user_id forgery, no second auth system

---

## 9. Implemented Features

> STEP 11 — notifications/realtime done.

- [x] Foundation — shell, health, i18n, theme
- [x] Database — PG, Alembic, User model
- [x] Auth — register/login/me/logout
- [x] Profiles — public PATCH own, avatar/cover + follow
- [x] Posts — create, user posts, patch/delete + hashtags
- [x] Feed/Social — global feed, likes/comments/reposts/bookmarks
- [x] Follow/Search — follow, search, hashtags
- [x] Stories — 24h image/video/text, grouped feed, viewer
- [x] Clubs — create, list/search, detail, join/leave, members, roles, avatar/cover
- [x] Channels/Messaging — ClubChannel + ClubMessage, 9 endpoints, ClubChannelPage
- [x] Notifications: model, service, API (list/unread-count/mark read/mark all/delete), follow/like/comment triggers, no self, frontend page + badge + realtime
- [x] Realtime: WebSocket manager, /ws auth, channel subscribe with membership IDOR, broadcast message.created/updated/deleted, notification.created, HTTP fallback, reconnect, dedup via message.id
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 509 kB, notifications/realtime ready
- Backend: Render/Railway — notifications/realtime ready, uploads, manager in-memory (no Redis)
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **206 passed** (25 auth + 8 db + 6 health + 29 posts + 18 profiles + 24 social + 21 follow/search + 16 stories + 23 clubs + 15 channels + 10 notifications + 11 realtime) ✅
  - notifications 10 (via follow, list own, cannot read other 403, unread count, mark read, mark all, no self like, like, comment, pagination)
  - realtime 11 (auth, unauth 4401, invalid token 4401, member subscribe, non-member error, cross-club error, event format, message created/updated/deleted broadcast, notification event)
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.23s
- Integration: `login → create club/channel → WS subscribe → HTTP post message → WS broadcast → notification via follow/like/comment → badge` via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- No Redis — manager in-memory, single instance only, not distributed (documented debt, future Redis Pub/Sub)
- No private DMs (future)
- No voice/video (future)
- No reactions/threads (future)
- No file attachments in messages (future)
- Hashtag ILIKE, Bookmarks 50 (known)
- Frontend chunks >500kB warning

---

## 13. Technical Debt

- Add Redis Pub/Sub for multi-instance scaling (debt, not now per spec §2)
- Add S3 (долг)
- Add cursor pagination for feed/search/notifications (offset)
- Add WebSocket presence/typing (future)
- Version single source (долг)

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP12.

---

## 15. Next Recommended STEP

**STEP 12 — Projects**

- projects model (name/description/tech/GitHub/demo/image/status), showcase, profile tab

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

---

## 17. Последний Git Commit

```
feat: STEP 11 — notifications and realtime (предстоит)
Branch: main | Status: clean (после commit)
Notifications/Realtime: model 008, service, 5+1 endpoints, manager, /ws, ClubChannelPage realtime, NotificationsPage/badge, 21 tests
```

---

## 18. Изменённые файлы (STEP 11)

```
[new] backend/app/models/notification.py
[mod] backend/app/models/__init__.py (+ Notification)
[new] backend/alembic/versions/008_create_notifications.py
[new] backend/app/services/notifications.py
[new] backend/app/api/v1/notifications.py
[mod] backend/app/api/v1/follows.py (+ notify)
[mod] backend/app/api/v1/posts.py (+ notify like)
[mod] backend/app/api/v1/comments.py (+ notify comment)
[mod] backend/app/api/v1/club_messages.py (+ broadcast)
[mod] backend/app/api/v1/router.py (+ notifications, realtime)
[new] backend/app/realtime/manager.py
[new] backend/app/api/v1/realtime.py
[new] backend/app/tests/test_notifications.py (10 tests)
[new] backend/app/tests/test_realtime.py (11 tests)
[new] frontend/src/api/notifications.ts
[new] frontend/src/hooks/useRealtime.ts
[new] frontend/src/pages/NotificationsPage.tsx
[mod] frontend/src/pages/ClubChannelPage.tsx (+ useChannelRealtime, status badge)
[mod] frontend/src/components/layout/AppShell.tsx (+ badge, useNotificationsRealtime)
[mod] frontend/src/App.tsx (+ /notifications)
[mod] backend/app/tests/test_realtime.py (engine file DB, separate http_client for broadcast)
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
