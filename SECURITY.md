# Bailanysta — SECURITY

> Дата: 2026-09-05 | STEP 14 — Security Hardening & Abuse Protection
> Этот документ фиксирует security principles и checklist, обязательные с первого дня (MASTER_PROMPT §31-§32).

---

## 1. Принципы

1. **Backend — source of truth.** Никакой авторизации/валидации только на фронте.
2. **Zero trust к входным данным.** Всё валидируется на бэке (Pydantic + ручные проверки).
3. **Least privilege.** Права проверяются на каждый мутационный запрос.
4. **No secrets in Git / frontend bundle.** Только env variables.
5. **Defense in depth.** Несколько слоёв: validation → auth → authorization → rate limit → headers.

---

## 2. Authentication & Session (§11)

| Мера | Детали | Статус |
|------|--------|--------|
| Password hashing | Argon2id (argon2-cffi `PasswordHasher` default: t=3, m=65536, p=4) | ✅ STEP3 implemented (`app/core/security.py:hash_password`) |
| Password policy | min 8, max 128, не логировать | ✅ Pydantic Field min 8, max 128 |
| Username/email uniqueness | DB unique constraints + 409 | ✅ `username`/`email` unique + 409 in `POST /auth/register` |
| Token storage | HttpOnly + Secure(prod)+SameSite=Lax cookie `access_token` access 15m | ✅ `set_auth_cookie` httponly, secure=is_production, samesite=lax, max_age 15m |
| CSRF | SameSite=Lax + CORS allow_credentials + конкретные origins (не *) | ✅ STEP3 decision (см. §CSRF) |
| Login brute force | Rate limit 20/min/IP (in-memory, single-instance) | ✅ STEP14 (`app/core/rate_limit.py`) — `auth_login` 20/60, `auth_register` 20/60 |
| Logout | Clear cookies (delete_cookie path=/) + 401 после | ✅ `POST /auth/logout` + `clear_auth_cookie` |
| Current user | `GET /auth/me` via `get_current_user` (cookie → JWT verify → DB → is_active) | ✅ `app/core/deps.py:get_current_user` |
| JWT | HS256, explicit algorithm, sub+exp+iat+type, SECRET_KEY from env, no alg=none | ✅ `app/core/security.py: create_access_token / decode_token` |

**Нельзя:** хранить пароли в открытом виде, хранить токены в localStorage без причины, отдавать хеш клиенту.

---

## 3. Authorization

- Каждый `PATCH /users/me`, `DELETE /posts/{id}`, `POST /clubs/{id}/...` проверяет `current_user.id == resource.owner_id` или роль.
- Club roles: `owner > admin > member` — проверяются на бэке, не на фронте.
- IDOR prevention: не доверять `user_id` из body, брать из токена; проверять принадлежность ресурса.
- 401 — не аутентифицирован, 403 — аутентифицирован но нет прав (MASTER_PROMPT §41).

---

## 4. Input Validation & Injection

- Pydantic schemas для всех входных данных (типы, длины, форматы).
- SQLAlchemy ORM + parameterized queries — никакого raw SQL с f-строками.
- XSS: React экранирует по умолчанию; для `dangerouslySetInnerHTML` — санитайз; backend — strip/escape для bio/post body если рендерится как HTML.
- Ограничение длины: post body ≤ 5000 chars, bio ≤ 500 chars, username 3-20.
- Hashtags/mentions — парсятся бэком, не фронтом.

---

## 5. File Upload Security (§32)

| Проверка | Детали |
|----------|--------|
| Size | avatar 2MB, post image 5MB, story 10MB — отклонять 413 |
| MIME | `image/jpeg, image/png, image/webp, image/gif` — проверять `file.content_type` + Pillow |
| Extension | allowlist, не blocklist |
| Filename | `uuid4() + ext`, игнорировать оригинальное имя |
| Content verify | `Pillow.Image.open().verify()` для изображений |
| Storage path | вне корня приложения, не исполняемая директория |
| No executables | `.php, .exe, .sh, .js` — никогда |
| Rate limit | limit uploads per user/min |

---

## 6. Network & Headers

- **CORS:** `CORS_ORIGINS` из env, конкретные домены в prod, `allow_credentials=True`, не `*` с credentials. Проверено `GET /api/v1/health` CORS headers ✅
- **CSRF:** `app/core/csrf.py` — Origin/Referer проверка для POST/PUT/PATCH/DELETE с cookies, `SameSite=Lax` + CORS, `403 CSRF check failed` если Origin not allowed. Тестируется `test_csrf_origin_blocked` ✅
- **Security headers (middleware `app/main.py: add_security_headers`):**
  - `X-Content-Type-Options: nosniff` ✅
  - `X-Frame-Options: DENY` ✅
  - `Referrer-Policy: strict-origin-when-cross-origin` ✅
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()` ✅ (STEP14)
  - `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none'` ✅ (безопасно, не ломает Vite)
  - `X-XSS-Protection: 0` ✅ (CSP preferred)
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` в prod ✅
  - Body size guard: `Content-Length >10MB → 413` ✅
  - Error handler: `HTTPException` preserved, generic `500 Internal server error` без stack trace/SQL leak ✅
- **Rate limiting:** `app/core/rate_limit.py` in-memory sliding window (single-instance, debt distributed) — см. §14, `429 Too many requests` ✅
- **HTTPS:** обязательно в prod (Vercel/Render дают автоматически).

---

## 7. Secrets Management (§7, §42)

- `.env` — никогда в Git (в .gitignore)
- `.env.example` — только ключи без значений
- `SECRET_KEY` — 32+ случайных байт, генерируется `openssl rand -hex 32`
- `DATABASE_URL` — только через env
- Frontend `VITE_*` — только публичные (API URL), никаких секретов.

---

## 8. Abuse Protection

- **Rate limit (STEP14 in-memory, single-instance, documented debt):**
  - `POST /auth/register` 20/min/IP (`auth_register`)
  - `POST /auth/login` 20/min/IP (`auth_login`) — `429` after 20
  - `POST /posts` 10/min/user (`post_create`)
  - `POST /posts/{id}/like` 30/min/user, `repost` 20/min, `bookmark` 30/min
  - `POST /posts/{id}/comments` 20/min/user
  - `POST /users/{username}/follow` 20/min/user
  - `POST /clubs` 10/min/user, `POST /clubs/.../messages` 30/min/user
  - `POST /users/me/projects` 10/min/user, `avatar/cover` 10/min/user
  - `POST /stories` 10/min/user
  - `GET /search` 30/min/IP (search abuse)
  - Store: `dict[key, deque[timestamps]]` sliding window, `X-Forwarded-For` support, `by_user` для auth’d endpoints, `429` JSON `{"detail":"Too many requests..."}` ✅, `clear_store()` для тестов, `autouse` fixture
- Pagination limits (`max_limit=50`, `ge=1 le=50` Pydantic) ✅
- Поиск — debounce 400ms на фронте + rate limit 30/min на бэке, `MAX_Q_LEN 100`, wildcard `%_` escaped `\_` `\%` ✅
- Логирование мутаций — для аудита (debt: structured logging)

---

## 9. Privacy & E2EE (§21)

- MVP: **не** заявлять E2EE, если не реализовано. Формулировка: "Privacy-focused architecture".
- Если E2EE позже: только проверенные библиотеки (libsodium, Web Crypto API), ключи — на клиенте, сервер — ciphertext, документировать threat model.
- Не писать "100% anonymous" / "невозможно взломать".

---

## 10. Checklist для каждого STEP

Перед merge каждого STEP проверять:

- [ ] Все новые endpoints требуют `get_current_user` где нужно
- [ ] Pydantic validation на все inputs
- [ ] Проверка ownership/role на мутациях
- [ ] Нет секретов в коде / логах / ответах API
- [ ] Upload validation если есть файлы
- [ ] Rate limit на чувствительные endpoints
- [ ] Корректные HTTP статусы (400/401/403/404/409/422/429/500)
- [ ] Frontend не показывает stack trace, а友好 сообщение
- [ ] `SECURITY.md` обновлён если добавилась новая поверхность атаки

---

## 11. Known Limitations (STEP 0)

- E2EE — отложено.
- CSP — базовая, будет ужесточаться после аудита фронтенда.
- 2FA — не в MVP, в roadmap.
- Content moderation (AI) — не в MVP.

---

## 12. Roadmap

- STEP 1: Argon2id, JWT cookies, CORS, базовые headers ✅ done
- STEP 2: DB + User model + Alembic ✅ done
- STEP 3: Authentication full (Argon2id, JWT HttpOnly, register/login/me/logout) ✅ done
- STEP 4: Profiles editor ✅ done
- STEP 5: Posts & Media ✅ done
- STEP 6: Feed & Social ✅ done
- STEP 7: Follow/Search ✅ done
- STEP 8: Stories ✅ done
- STEP 9: Clubs ✅ done
- STEP 10: Channels/Messaging ✅ done
- STEP 11: Notifications & Realtime (WS, manager, no Redis) ✅ done
- STEP 12: Projects ✅ done
- STEP 13: i18n/Theme/Responsive ✅ done
- STEP 14: Security Hardening (rate limiting, CSRF, headers, XSS, upload, WS, etc) ✅ done
- STEP 15: Testing & Performance (next)

## 13. STEP 3 — CSRF Decision

Хранится в HttpOnly cookie `access_token`, поэтому классический CSRF возможен.

Принято (STEP3, без over-engineering):
- `SameSite=Lax` (default) — блокирует cross-site POST с других доменов, но разрешает top-level navigation
- `CORS` — `allow_credentials=True`, `allow_origins` из `CORS_ORIGINS` env (не `*`), конкретные домены `http://localhost:5173` в dev, прод домены configurable
- `Secure` — `true` в `production` (HTTPS), `false` в dev для localhost
- `HttpOnly` — `true` всегда, JS не читает токен (XSS mitigation)
- `Path=/`, `Max-Age=900` (15m)

Не делается в STEP3:
- Double-submit CSRF token (требует фронтенд state + extra endpoint, добавим если будет cross-site deployment с сторонними origins)
- `SameSite=Strict` — ломает UX при переходах с внешних ссылок

Документировано здесь; `ARCHITECTURE.md §6` дублирует flow.

## 14. STEP 3 — Abuse / Rate Limit Status (обновлено STEP14)

Auth endpoints чувствительны (brute-force).

STEP3 — базовая защита без внешней инфраструктуры:
- Uniform `401 Invalid credentials` (не раскрывает существование email/username)
- Password не логируется, не возвращается
- 409 на duplicate (не 500)
- Validation max lengths (username 50, password 128) — reject huge payloads

STEP14 — реализован `app/core/rate_limit.py` in-memory sliding window (single-instance, debt distributed). Лимиты см. §8. Тесты `test_rate_limit_login` (21→429) и `test_rate_limit_search` (31→429) ✅. `clear_store()` autouse в `conftest.py` для изоляции тестов.

## 15. STEP 10 — Channels / Messages Security

**Channel membership:** `GET /clubs/{slug}/channels` requires member (403 else), ordered position, no duplicate slug per club (Unique), position auto max+1, no negative.

**Channel permissions:** `POST/PATCH/DELETE` owner/admin only (403 member/moderator), `member_role` check via ClubMember, no privilege escalation, IDOR via club_id check (channel must belong to club).

**Messages:** `GET /messages` member 403, limit 50 le100 offset, ordered asc, author joined (no N+1), `POST` member 403, content trim 1-10000, author current_user (no author_id bypass), `PATCH` owner only 403 other, `DELETE` author or owner/admin/moderator (member cannot delete other), IDOR via `message.channel_id == channel.id` (forged channel 404), cross-club 404/403.

**Content:** plain text, no raw HTML, React escape, XSS safe, no `dangerouslySetInnerHTML`.

**Storage:** no attachments in MVP (future), channels not executable, no path traversal (slugify), UUID not needed for messages (already UUID).

**Realtime:** not in STEP10 — HTTP only, no WebSocket, no Redis, documented for STEP11.

## 16. STEP 11 — Notifications & Realtime Security

**WebSocket auth:** same `decode_token` (HS256, explicit alg, sub, type, is_active), `?token=` query or `access_token` HttpOnly cookie, `is_active` check, `type==access`, close 4401 on fail, no user_id forgery, no second auth system, no `alg=none`.

**Channel authorization:** `subscribe` requires `channel_id` UUID, verify `ClubChannel` exists + `ClubMember` membership (`ClubMember.club_id == channel.club_id, user_id == current_user.id`), cross-club 404/403, not member 403, `channel_id` required, `Invalid channel_id` 422, `Channel not found` 404, `Not a member` 403, `Unknown type` error, payload max 10k.

**Notifications IDOR:** `GET /notifications` only own (`recipient_id == current_user.id`), `GET /unread-count` only own, `PATCH /{id}/read` checks `recipient_id == current_user.id` (403 else), `POST /read-all` only current, `DELETE /{id}` only own, `actor_id` cannot be forged (backend determines from `current_user`), no private fields leak, no self-notification (follow/like/comment check `recipient != actor`).

**Realtime notifications:** `manager.send_to_user` only to `recipient_id`'s `user_connections`, `notification.created` event only to that user, no broadcast to others, `is_read` false initially, no secrets in payload.

**Message realtime:** `POST /clubs/.../messages` DB commit before `manager.broadcast_channel` (no ghost), `broadcast_channel` to `channel_subscribers` only (member check at subscribe time, not at broadcast, but channel membership already verified at subscribe, and broadcast is to channel's subscribers which are members), dedup via `message.id` on frontend, no HTML (text), XSS safe, max 10k, no giant JSON, `message.updated`/`deleted` similarly.

**Rate/abuse:** WS max payload 10k, invalid JSON → error, unknown type → error, no giant payload, HTTP message limits already 1-10000, no bypass via WS (WS only subscribes, not creates messages via WS; creation via HTTP POST, so HTTP validation still applies, no WS message creation endpoint to bypass).

**No Redis:** in-memory `manager` (user_connections, channel_subscribers, Lock) — single instance only, documented debt for future Redis Pub/Sub, no distributed event bus, no Celery, no Socket.IO.

## 17. STEP 12 — Projects Security

**Ownership / IDOR:** `POST /users/me/projects` ignores any `owner_id` from client (`owner_id = current_user.id`), `PATCH/DELETE/POST .../image` check `project.owner_id == current_user.id` (403 else) via DB, `GET /users/{username}/projects` public but `GET /users/me/projects` requires auth, `GET /projects/{id}` public but mutation only via `/users/me/projects/{id}` with owner check, UUID not auth, no escalation.

**URL validation:** `github_url` must be `https://` or `http://` + host `github.com`/`www.github.com` (Pydantic `_validate_url` + urlparse, reject `javascript:`/`data:`/`file:`), `demo_url` allows any `https`/`http` but same scheme reject, max 512, both Pydantic Field, no SSRF (no HTTP fetch during validation, just parse), no `dangerouslySetInnerHTML` (React escape, whitespace-pre-wrap).

**Technologies:** max 20, each max 50 chars, trim, dedup case-insensitive, no taxonomy table (MVP), stored as JSON (Postgres JSON / SQLite TEXT), no injection (Pydantic list of str).

**Status:** limited enum `idea/in_progress/completed/archived` (Pydantic enum), no arbitrary values, no DB enum to keep SQLite compat, validated before DB.

**Image upload:** `POST /users/me/projects/{id}/image` owner only 403, uses `services/storage.py:save_image` (Pillow verify, MIME allowlist jpeg/png/webp, UUID hex filename, safe_subdir projects alphanumeric, 5 MB via `_validate_size` 413, no path traversal `../../` → safe, no overwrite, stored `uploads/projects/` gitignored, old file best-effort delete after DB commit, public_url `/uploads/projects/<uuid>.ext` served via StaticFiles no exec).

**Search:** `q` trim max 100, parameterized `like` (SQLAlchemy), no raw f-string, ILIKE via `func.lower().like`, cast technologies to String for SQLite compat, limit 50, no giant payload.

**No GitHub API:** no OAuth, no token, no repository sync, no code hosting, only showcase links — documented to avoid false security claims.

**Rate/performance:** pagination 50, no N+1 (projects single query ordered by position+created), no external HTTP during list, no E2EE/private DM.

## 18. STEP 14 — Security Hardening & Abuse Protection

**Дата:** 2026-09-05 | **Цель:** audit + hardening без новых фич, подготовка к Testing & Performance.

**Authentication audit:** Argon2id `PasswordHasher` default `t=3 m=65536 p=4` ✅, JWT `HS256` explicit `algorithms=[HS256]` no `alg=none` ✅, `jwt.decode` с `SECRET_KEY` из env ✅, `sub` UUID + `exp` 15m + `iat` + `type=access` ✅, `verify_password` constant-time ✅, cookie `HttpOnly=True Secure=is_production SameSite=Lax Path=/ Max-Age=900` ✅, `decode_token` raises 401 на malformed/expired/missing/user-not-found/inactive/wrong-type ✅, `logout` `delete_cookie Path=/` ✅, тесты `test_malformed_token_rejected`, `test_expired_token_rejected`, `test_none_alg_rejected`, `test_nonexistent_user_token_rejected`, `test_wrong_type_token_rejected` ✅.

**CSRF:** `SameSite=Lax` + `CORS allow_credentials` конкретные origins ✅, дополнительно `app/core/csrf.py` Origin/Referer проверка для POST/PUT/PATCH/DELETE с cookies → `403 CSRF check failed` если Origin not allowed ✅, middleware `csrf_middleware` в `main.py` ✅, тесты `test_csrf_origin_blocked` (evil.com→403) vs `test_csrf_same_origin_allowed` (localhost:5173→201) ✅.

**Authorization/IDOR:** полный аудит 14 ресурсов (users, posts, comments, likes, reposts, bookmarks, follows, stories, clubs, club_members, channels, messages, notifications, projects, uploads, WS). Все мутации проверяют `owner_id == current_user.id` или `ClubMember` role, `user_id` из токена, не из body ✅. Тесты: `test_idor_post_other_user` 403, `test_idor_project_other_user` 403, `test_idor_notification_other_user` 403, `test_cross_club_channel_access` 404/403 ✅.

**Club privileges:** матрица `owner>admin>moderator>member` проверена: member cannot `POST /channels` 403 ✅, moderator cannot `PATCH .../role admin` 403 ✅, admin cannot `PATCH .../role owner` 403/422 ✅, нельзя self-promote ✅, `owner` cannot be removed ✅, nested `club→channel→message` IDOR через `channel.club_id == club.id` ✅. Тесты `test_member_cannot_create_channel`, `test_moderator_cannot_promote_to_admin`, `test_admin_cannot_assign_owner` ✅.

**Rate limiting:** in-memory sliding window `app/core/rate_limit.py` — `store: dict[str, deque[float]]`, `X-Forwarded-For` IP, `by_user` для auth’d endpoints, `429` ✅. Лимиты см. §8. Debt: single-instance, no Redis (документировано). Тесты `test_rate_limit_login` 21→429, `test_rate_limit_search` 31→429 ✅, `clear_store` autouse ✅.

**Input hardening:** Pydantic `max_length`/`ge`/`le`/`pattern` на всех schemas (post 1-10000, comment 1-2000, username 3-50 regex, bio 500, club name 2-100, project name 150 etc) ✅, `Query(..., ge=1, le=50)` для pagination ✅, `str.strip()` для всех строк ✅, `MAX_Q_LEN 100` ✅, `position` int bounds ✅, `Unknown fields` ignored (`extra="ignore"` in Settings) ✅. Тесты `test_invalid_uuid_rejected` 422, `test_pagination_limits` 422, `test_oversized_content_rejected` 422, `test_invalid_enum_rejected` 422 ✅.

**XSS:** React по умолчанию экранирует, `dangerouslySetInnerHTML` не используется (grep 0) ✅, `post/comment/message/bio/club/project` хранятся как plain text, `whitespace-pre-wrap break-words` ✅, URL рендер через `<a>` с `rel="noopener noreferrer"` ✅, тест `test_xss_stored_not_executed` `<script>` хранится как plain ✅.

**URL security:** `schemas/project.py` `_validate_url` `urlparse` scheme `https/http` only + `github.com` host check + reject `javascript/data/file/vbscript` ✅, тест `test_url_scheme_rejected` 422 ✅.

**File upload:** `services/storage.py` — `MAX_MB 5`, `ALLOWED_MIME jpeg/png/webp`, `Pillow verify` + format→ext, `UUID hex` + `safe_subdir` alphanumeric, no `../`/`null bytes`, `no executables` (SVG `image/svg+xml` → 415) ✅, 10 MB global `Content-Length` guard в `main.py` →413 ✅, тесты `test_upload_oversized` 413/415, `test_upload_wrong_mime` 415, `test_upload_path_traversal_safe` no `../`, `test_svg_blocked` 415 ✅.

**Headers:** CSP `default-src 'self'` etc ✅, `Permissions-Policy` ✅, `X-XSS-Protection 0` ✅, `HSTS` prod ✅, CORS not `*` with credentials ✅, body size guard 10MB ✅, error handler preserves `HTTPException` detail, generic `500 Internal server error` без stack trace ✅, тест `test_security_headers_present` + `test_error_not_leak_stack` ✅.

**Error leakage:** `global_exception_handler` возвращает `{"detail":"Internal server error"}` для `Exception`, но `HTTPException` пробрасывается с safe detail ✅, no secrets/paths/SQL leak ✅.

**WebSocket:** `realtime/manager.py` + `realtime.py` — `decode_token` HS256 + `is_active` + `type==access` + `4401` on fail ✅, `subscribe` checks `ClubChannel` exists + `ClubMember` membership `club_id` + `user_id` ✅, cross-club 404/403 ✅, `message.created` only после `DB commit` ✅, `max payload 10k` ✅, тест `test_ws_invalid_token_rejected` 4401, `test_ws_cross_club_subscription_blocked` 403 via HTTP (покрывает IDOR) ✅.

**Notification privacy:** `recipient_id == current_user.id` для list/unread-count/read/read-all/delete ✅, `actor` не leak email/hash ✅, `is_read` false initially ✅, тест `test_notification_unread_count_own_only` ✅.

**Search abuse:** `MAX_Q_LEN 100` + `escape_like` `%`→`\%` `_`→`\_` + `escape="\\"` в `like` ✅, `limit le50` ✅, `rate limiting 30/min` ✅, parameterized `SQLAlchemy` no raw f-string ✅, тест `test_search_wildcard_escaped` `%` не возвращает все ✅.

**DB security:** ORM `parameterized` ✅, no raw SQL, `ownership filters` на все мутации ✅, `FK CASCADE` + `UNIQUE` ✅.

**Secrets/config:** `.env` в `.gitignore` ✅, `.env.example` без secrets ✅, `SECRET_KEY` placeholder `"change-me-..."` ✅, `VITE_API_URL` только public ✅, `debug` true dev false prod ✅, `git log` no secrets ✅.

**Dependency hygiene:** `pip check` no broken deps, `npm audit` moderate esbuild (low risk, documented) ✅, outdated check via `pip list --outdated` (no critical CVE for FastAPI/SQLAlchemy/Pillow) ✅.

**Known limitations MVP (single-instance):** in-memory rate limiter, WS single-instance, local uploads (no S3), offset pagination (no cursor), documented ✅.
