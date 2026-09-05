# Bailanysta — SECURITY

> Дата: 2026-09-05 | STEP 11 — Notifications & Realtime
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
| Login brute force | Rate limit 5/min/IP | ⚠️ Debt — архитектура готова, full rate limiter в STEP14 (см. Abuse Protection) |
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

- **CORS:** `CORS_ORIGINS` из env, конкретные домены в prod, `allow_credentials=True`, не `*` с credentials.
- **Security headers (middleware):**
  - `Strict-Transport-Security: max-age=63072000` (в prod с HTTPS)
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy` (базовая, ужесточать позже)
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Rate limiting:** slowapi / custom — на auth, post creation, search, uploads.
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

- Rate limit по IP + по user
- Pagination limits (`max_limit=50`)
- Поиск — debounce на фронте + rate limit на бэке
- Подозрительные паттерны (спам постов) — лимит 10 постов/час на MVP
- Логирование мутаций (кто, когда, что) — для аудита

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
- STEP 14: Rate limiting (full), pagination limits, IDOR hardening
- STEP 14+: Club permissions, security headers audit

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

## 14. STEP 3 — Abuse / Rate Limit Status

Auth endpoints чувствительны (brute-force).

STEP3 — базовая защита без внешней инфраструктуры:
- Uniform `401 Invalid credentials` (не раскрывает существование email/username)
- Password не логируется, не возвращается
- 409 на duplicate (не 500)
- Validation max lengths (username 50, password 128) — reject huge payloads

Full rate limiting (5/min/IP на login, счётчик неудач, slowapi/redis) — отложено в STEP14 как **security debt**, т.к. требует инфраструктуры (Redis / in-memory store) и не должно блокировать auth foundation. Архитектура готова: middleware место зарезервировано в `app/main.py`, `SECURITY.md §8`.

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
