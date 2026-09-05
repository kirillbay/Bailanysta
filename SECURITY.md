# Bailanysta — SECURITY

> Дата: 2026-09-05 | STEP 0
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

| Мера | Детали | Статус (STEP 0) |
|------|--------|-----------------|
| Password hashing | Argon2id (argon2-cffi), не bcrypt, не plain | Planned |
| Password policy | min 8, проверка на common passwords (опционально) | Planned |
| Username/email uniqueness | DB unique constraints + 409 Conflict | Planned |
| Token storage | HttpOnly + Secure + SameSite=Lax cookies (access 15m, refresh 7d) | Planned |
| CSRF | SameSite + Origin check + optional double-submit | Planned |
| Login brute force | Rate limit на `/auth/login` (5/min/IP), счётчик неудач | Planned |
| Logout | Clear cookies + refresh token revocation (если храним) | Planned |
| Current user | `GET /auth/me` с dependency `get_current_user` | Planned |

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

- STEP 1: Argon2id, JWT cookies, CORS, базовые headers
- STEP 2: Authorization на posts/comments, upload validation
- STEP 3: Rate limiting, pagination limits, IDOR тесты
- STEP 4+: WS auth, club permissions, security headers audit
