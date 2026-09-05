# Bailanysta — Social platform for IT communities

> Modern, minimal, premium social network for developers, designers, AI/ML engineers, DevOps, QA, founders and everyone passionate about technology.

![Status](https://img.shields.io/badge/status-STEP%200%20%E2%80%94%20initialized-blue)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI%20%2B%20PostgreSQL-0ea5e9)
![i18n](https://img.shields.io/badge/i18n-ru%20%7C%20kk%20%7C%20en-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Live demo:** *deploy planned in upcoming STEPs — Vercel (frontend) + Render/Railway (backend) + Neon (PostgreSQL)*

---

## ✨ Overview

**Bailanysta** answers one question:

> *“What’s happening in the life and work of the IT community?”*

Users can:
- Share thoughts, photos, GitHub links and project showcases
- Follow people, like / comment / bookmark / repost
- Read a chronological feed with cursor pagination
- Create 24h stories
- Join **Clubs** — Discord-like IT communities with channels (Python Kazakhstan, AI Engineers, Frontend, DevOps…)
- DM and club chat (WebSocket-ready architecture)
- Get notifications, search users/posts/clubs/hashtags, manage projects on profile
- Switch language **🇷🇺 Русский / 🇰🇿 Қазақша / 🇬🇧 English** and theme **☀️ Light / 🌙 Dark**

Inspired by the best of Threads (feed), Telegram (DM), Discord (clubs), GitHub (identity) and Reddit (discussions) — but with its own visual and product identity.

---

## 🚀 Features

| Area | MVP (P1) | Next (P2) | Future (P3) |
|------|----------|-----------|-------------|
| Core | Auth, profiles, posts, feed, likes/comments/follows | — | — |
| Social | Bookmarks, hashtags, mentions | Stories, search, projects | Recommendations |
| Communities | — | Clubs + channels + roles | Voice channels |
| Messaging | — | DMs, club messages, notifications | E2EE, realtime WS |
| UX | Responsive, skeletons, i18n, dark/light | — | Mobile app |

See `PROJECT_STATE.md` for current progress.

---

## 🧱 Tech Stack

**Frontend:** React + TypeScript + Vite + Tailwind CSS + shadcn/ui + Lucide + Framer Motion + React Router + TanStack Query + React Hook Form + Zod + i18next

**Backend:** Python + FastAPI + SQLAlchemy 2.x + Pydantic v2 + Alembic + PostgreSQL + Argon2id + JWT (HttpOnly cookies)

**Infra (planned):** Vercel (frontend) · Render/Railway/Fly.io (backend) · Neon/Supabase (Postgres) · R2/S3 (storage)

Why this stack? See [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## 🏗 Architecture

```
Browser (React SPA, i18n, TanStack Query)
   ↕ HTTPS / JSON / WS (credentials: include)
Backend API (FastAPI /api/v1/*)
   ↕
PostgreSQL · Storage (S3/R2) · External APIs (server-side only)
```

- Frontend never talks to DB or external services directly — all through Backend (§61 MASTER_PROMPT).
- Auth: Argon2id + JWT access (15m) + refresh (7d) in `HttpOnly + Secure + SameSite=Lax` cookies.
- Pagination: cursor-based for feed.
- i18n from day one: `frontend/src/locales/{ru,kk,en}.json`.
- File uploads validated (MIME, size, Pillow verify, uuid filenames).

Detailed design → [`ARCHITECTURE.md`](./ARCHITECTURE.md) · Security → [`SECURITY.md`](./SECURITY.md)

---

## 📦 Project Structure

```
Bailanysta/
├── frontend/               # Vite + React app (scaffold in STEP 1)
│   └── src/
│       ├── api/
│       ├── components/ui/
│       ├── features/
│       ├── pages/
│       ├── locales/        # ru.json, kk.json, en.json
│       └── lib/
├── backend/                # FastAPI app (scaffold in STEP 1)
│   └── app/
│       ├── core/           # config, security
│       ├── database/
│       ├── models/
│       ├── schemas/
│       ├── api/v1/
│       └── services/
├── docs/
├── MASTER_PROMPT.md        # Source of truth (68 sections)
├── PROJECT_STATE.md        # Persistent memory — read this first!
├── ARCHITECTURE.md
├── SECURITY.md
├── .env.example
└── README.md
```

---

## ⚡ Quick Start (after STEP 1)

> **Current:** STEP 0 — workspace initialized, no runnable code yet. Instructions below will work starting STEP 1.

### Prerequisites

- Node.js 20+ · Python 3.12+ · PostgreSQL 15+ (or Docker) · Git

### 1. Clone

```bash
git clone https://github.com/<you>/bailanysta.git
cd bailanysta
```

### 2. Environment

```bash
cp .env.example .env
# fill DATABASE_URL, SECRET_KEY, CORS_ORIGINS, etc.
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs (Swagger)
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 5. With Docker (planned)

```bash
docker-compose up --build
```

---

## 🔧 Environment Variables

See [`.env.example`](./.env.example) for full list.

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@localhost:5432/bailanysta` | Postgres DSN |
| `SECRET_KEY` | `openssl rand -hex 32` | JWT signing key |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins (comma-separated) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `VITE_API_URL` | `http://localhost:8000` | Frontend → Backend URL |

Never commit `.env` — only `.env.example`.

---

## 🛠 Development

- **Before every STEP:** read `PROJECT_STATE.md` + `ARCHITECTURE.md`, inspect current code, then change.
- **After every STEP:** tests + lint + build + manual check + update `PROJECT_STATE.md`.
- **Conventions:** no giant files, no fake functionality (§52), no breaking existing API without reason (§51).
- **Seed data:** `backend/scripts/seed.py` (not hardcoded in frontend).

### Useful commands (from STEP 1)

```bash
# backend
pytest -q
alembic revision --autogenerate -m "add posts"
alembic upgrade head

# frontend
npm run lint
npm run build
npm run preview
```

---

## 🚢 Deployment

| Component | Recommended | Alternatives |
|-----------|-------------|--------------|
| Frontend | Vercel | Netlify |
| Backend | Render / Railway | Fly.io |
| Database | Neon | Supabase, Railway PG |
| Storage | Cloudflare R2 | AWS S3 |

Check current free tiers before deploying (§43). Production secrets via hosting dashboard, not Git.

---

## 🎨 Design Process

- **Direction:** modern · minimal · premium · developer-oriented — not sterile, not admin-panel, content-first.
- **Responsive:** sidebar → bottom nav on mobile, feed max 640-680px, skeletons/empty/error states everywhere.
- **Accessibility:** semantic HTML, keyboard nav, focus states, aria, contrast.
- **Branding:** wordmark "Bailanysta" (Kazakh: *байланыста* — "in connection / in touch"), simple logomark, no trademark infringement.

---

## 🔐 Security

Implemented/planned (see `SECURITY.md`):

- Argon2id hashing, HttpOnly Secure SameSite cookies, CSRF protection
- Pydantic validation + ORM parameterized queries (no SQL injection)
- Backend authorization on every mutation, IDOR prevention
- CORS allowlist, security headers, rate limiting, XSS prevention
- Upload validation (MIME, size, Pillow verify, uuid filenames, no executables)
- No secrets in Git or frontend bundle

---

## ⚖️ Trade-offs

- **Cookie JWT vs localStorage:** chosen cookie (XSS-safer, needs CSRF).
- **Cursor vs offset pagination:** cursor (no duplicates on new posts).
- **Postgres-only migrations:** honest prod parity, slightly harder dev.
- **Polling → WebSocket:** polling for MVP, WS later without breaking API.
- **Simple first, optimize later:** ship stable P1 before P2/P3.

---

## 🐛 Known Issues & Limitations

- STEP 0 — no runnable app yet; tracking in `PROJECT_STATE.md`.
- E2EE not implemented (privacy-focused architecture, not E2E yet — see SECURITY.md §9).
- Voice channels: schema placeholder only until P1 stable.

---

## 🗺 Roadmap

**P1 (must, deadline 2026-09-06 23:59 Almaty):** auth, profiles, posts, feed, interactions, backend+DB, deployment, responsive, i18n

**P2:** clubs, stories, DMs, notifications, search, projects, bookmarks

**P3:** realtime WS, voice, E2EE, recommendations, job board, events, mobile app, GitHub integrations

See MASTER_PROMPT §55 and `PROJECT_STATE.md` §12.

---

## 📄 Documentation

- [`MASTER_PROMPT.md`](./MASTER_PROMPT.md) — full product & engineering spec (68 sections)
- [`PROJECT_STATE.md`](./PROJECT_STATE.md) — persistent memory, current STEP
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — architecture decisions
- [`SECURITY.md`](./SECURITY.md) — security checklist

---

## 🤝 Contributing

Public GitHub repo — PRs welcome after initial deploy. Keep history clean, never commit `.env` or `node_modules`.

---

## 📜 License

MIT — see `LICENSE` (to be added in STEP 1).

---

<p align="center">Built with care for the IT community. Байланыста болайық — stay in touch.</p>
