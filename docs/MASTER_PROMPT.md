# BAILANYSTA — MASTER PROJECT PROMPT
## 0. ТВОЯ РОЛЬ

Ты — основной автономный разработчик проекта Bailanysta.

Ты работаешь над полноценным веб-приложением социальной сети для IT-комьюнити.

Твоя задача в рамках этого проекта — не просто писать код, а последовательно спроектировать, реализовать, протестировать, обезопасить и подготовить к публичному деплою полноценное production-like веб-приложение.

ВАЖНО:

Этот документ является ознакомительным MASTER PROMPT.

На данном этапе:

1. Создай рабочее пространство проекта.
2. Изучи и проанализируй весь этот документ.
3. Зафиксируй его в рабочей директории проекта.
4. Создай необходимые файлы состояния проекта и документации.
5. Подготовь архитектурный план.
6. НЕ начинай массовую реализацию функциональности, пока не получишь отдельную команду на первый этап разработки.
7. После подготовки сообщи кратко, что контекст изучен, рабочее пространство создано, план понятен и ты готов получить STEP 1.

Не пытайся самостоятельно реализовать весь проект сразу.

Работа будет выполняться поэтапно.

---

# 1. КОНЦЕПЦИЯ ПРОЕКТА

Название:

# Bailanysta

Рабочая концепция:

> Bailanysta — социальная платформа для IT-комьюнити.

Это не должен быть очередной клон Twitter/X, Threads, Reddit, Discord или Telegram.

Мы берём лучшие концепции из разных продуктов и объединяем их в единую IT-ориентированную социальную платформу.

Условные источники вдохновения:

* Threads — простая социальная лента и публикации;
* Telegram — удобное личное общение;
* Discord — тематические сообщества/клубы и каналы;
* GitHub — профессиональная IT-идентичность и проекты;
* Reddit — тематические обсуждения и сообщества.

Но Bailanysta должна иметь собственную визуальную и продуктовую идентичность.

---

# 2. ГЛАВНАЯ ЦЕЛЬ

Создать настоящую публичную социальную платформу, которой потенциально могут пользоваться реальные люди.

Это НЕ локальная демонстрация.

Это НЕ просто учебный CRUD.

Это НЕ набор статических страниц.

После деплоя пользователь должен иметь возможность открыть сайт через интернет, зарегистрироваться, создать аккаунт, заполнить профиль, подписаться на пользователей, создавать публикации, взаимодействовать с ними, находить сообщества, общаться и использовать другие функции приложения.

Приложение должно быть рассчитано прежде всего на IT-аудиторию:

* разработчики;
* AI/ML специалисты;
* DevOps;
* QA;
* аналитики;
* дизайнеры;
* cybersecurity специалисты;
* студенты IT;
* founders;
* product managers;
* системные администраторы;
* начинающие специалисты;
* опытные специалисты;
* люди, интересующиеся технологиями.

---

# 3. ОСНОВНОЙ ПРИНЦИП ПРОДУКТА

Bailanysta должна отвечать на вопрос:

> «Что происходит в жизни и работе IT-комьюнити?»

Пользователь должен иметь возможность:

* поделиться мыслями;
* опубликовать фотографию;
* рассказать о своём проекте;
* поделиться ссылкой на GitHub;
* спросить совета;
* обсудить проблему;
* найти единомышленников;
* найти IT-клуб;
* вступить в сообщество;
* общаться в клубе;
* писать личные сообщения;
* подписываться на интересных людей;
* читать ленту;
* создавать stories;
* получать уведомления;
* сохранять полезные публикации;
* искать пользователей, посты, клубы и темы.

---

# 4. ЧЕГО НЕ НУЖНО ДЕЛАТЬ

В текущей версии НЕ нужно реализовывать отдельный полноценный редактор/публикацию исходного кода как замену GitHub.

Пользователи должны иметь возможность просто публиковать ссылки на:

* GitHub;
* GitLab;
* другие репозитории;
* проекты;
* сайты;
* demo.

Мы НЕ строим второй GitHub.

Также НЕ нужно сейчас добавлять AI-помощника для генерации постов, кода или другого контента.

AI-функциональность можно рассматривать как потенциальное будущее расширение, но в текущем MVP она отсутствует.

Главная задача сейчас — качественная социальная платформа.

---

# 5. ЦЕЛЕВЫЕ ЯЗЫКИ

Приложение должно поддерживать три языка:

1. Русский
2. Қазақша
3. English

Локализация должна быть заложена в архитектуру С САМОГО НАЧАЛА.

Нельзя писать интерфейс так, чтобы потом пришлось вручную переписывать все компоненты.

Необходимо использовать полноценную систему i18n.

Например:

frontend/src/locales/

или другую архитектурно корректную структуру.

Все пользовательские UI-строки должны находиться в translation resources.

Переключение языка должно работать непосредственно внутри приложения.

Выбор языка пользователя должен сохраняться.

При первом посещении можно использовать язык браузера, если это удобно архитектурно.

---

# 6. WEB-FIRST

Проект является веб-приложением.

Он НЕ должен зависеть от локального компьютера разработчика.

Необходимо проектировать приложение так, чтобы:

Frontend:

* мог быть размещён в cloud hosting;
* обращался к backend через публичный API.

Backend:

* работал на удалённом сервере;
* имел доступ к production database;
* корректно обрабатывал API requests.

Database:

* находилась в облаке в production.

Локальная среда нужна только для разработки.

После деплоя приложение должно быть доступно через интернет.

---

# 7. ПУБЛИЧНЫЙ GITHUB

Проект должен быть подготовлен к размещению в публичном GitHub repository.

Репозиторий должен содержать:

README.md

исходный код frontend/backend,

конфигурацию проекта,

.env.example,

тесты,

документацию,

инструкции запуска,

архитектурную документацию,

описание известных ограничений.

НИКОГДА не помещай реальные:

* API keys;
* passwords;
* database credentials;
* JWT secrets;
* private keys;
* production secrets;

в Git repository.

Используй environment variables.

---

# 8. РЕКОМЕНДУЕМЫЙ TECH STACK

Предпочтительный стек:

## Frontend

React

TypeScript

Vite

Tailwind CSS

shadcn/ui или аналогичная качественная component system

Lucide Icons

Для анимаций при необходимости:
Framer Motion

Для routing:
React Router

Для server state/data fetching:
TanStack Query

Для forms:
React Hook Form

Для validation:
Zod

Для internationalization:
i18next + react-i18next

Можно изменить отдельные библиотеки, если есть объективная техническая причина.

Но НЕ усложняй стек без необходимости.

---

# 9. BACKEND

Предпочтительный backend:

Python

FastAPI

SQLAlchemy 2.x

Pydantic

Alembic

PostgreSQL

Backend должен быть разделён логически:

* API routes;
* schemas;
* services;
* models;
* database;
* authentication;
* authorization;
* configuration;
* utilities.

Не создавать один огромный файл main.py.

---

# 10. DATABASE

Production database:

PostgreSQL.

Development может использовать PostgreSQL или SQLite только если это действительно удобно.

Но архитектура должна быть совместима с PostgreSQL.

Предполагаемые основные сущности:

* users;
* profiles;
* posts;
* post_media;
* comments;
* likes;
* follows;
* stories;
* story_views;
* clubs;
* club_members;
* club_channels;
* club_messages;
* conversations;
* conversation_members;
* messages;
* notifications;
* hashtags;
* post_hashtags;
* bookmarks;
* projects;
* sessions/authentication-related entities.

Это НЕ окончательная схема.

Перед реализацией каждого крупного модуля необходимо проектировать связанные сущности логично.

Не создавать таблицы «на всякий случай».

---

# 11. AUTHENTICATION

Необходимо реализовать нормальную регистрацию и авторизацию.

Минимально:

* регистрация;
* login;
* logout;
* password hashing;
* session/token management;
* protected routes;
* current user endpoint;
* password validation;
* username uniqueness;
* email uniqueness.

Для хранения паролей использовать современный безопасный password hashing algorithm.

Предпочтительно Argon2id.

НЕ хранить пароли в открытом виде.

Не хранить access tokens небезопасно в localStorage, если архитектура позволяет использовать более безопасную cookie-based схему.

Предпочтение:

HttpOnly + Secure + SameSite cookies.

Архитектура authentication должна учитывать CSRF protection там, где это необходимо.

---

# 12. ПРОФИЛИ

Каждый пользователь должен иметь полноценный профиль.

Профиль содержит:

* avatar;
* cover image;
* display name;
* username;
* bio;
* location;
* role;
* skills;
* interests;
* GitHub link;
* LinkedIn link;
* personal website;
* projects;
* followers;
* following;
* posts.

Пользователь должен иметь возможность редактировать свой профиль.

Аватар и обложка должны загружаться через backend/storage architecture.

Не хранить большие бинарные файлы непосредственно в PostgreSQL без объективной необходимости.

---

# 13. POSTS

Основная социальная единица — публикация.

Пользователь может создавать публикацию.

Публикация может содержать:

* текст;
* изображения;
* несколько изображений;
* GIF;
* ссылку;
* GitHub/GitLab URL;
* hashtags;
* mentions.

Основная цель — сделать публикации максимально похожими на современную социальную сеть.

Не превращать composer в сложную форму.

Пользователь должен открыть:

"+ Создать"

и просто написать публикацию.

---

# 14. POST INTERACTIONS

Обязательные социальные механики:

* Like;
* Comment;
* Repost;
* Share;
* Bookmark;
* Follow;
* Mention;
* Hashtag.

При необходимости можно использовать optimistic UI там, где это безопасно.

Например:

Like должен ощущаться мгновенным.

Но frontend не должен скрывать реальную ошибку backend.

Если сервер отклонил операцию — состояние UI должно корректно откатиться.

---

# 15. FEED

Главная страница должна содержать feed.

В feed отображаются:

* публикации подписок;
* релевантные публикации;
* популярные публикации;
* возможно рекомендации.

На MVP можно начать с хронологической ленты.

Алгоритмическую персонализацию не нужно делать слишком сложной.

Главное:

* корректность;
* производительность;
* pagination;
* отсутствие дублей;
* loading state;
* error state;
* empty state.

Предпочтительно использовать cursor-based pagination там, где это архитектурно оправдано.

---

# 16. STORIES

Необходимо предусмотреть stories как одну из социальных функций.

Stories:

* изображение;
* короткое видео;
* текст;
* timestamp;
* expiration.

По умолчанию story живёт 24 часа.

Пользователь может:

* создавать;
* просматривать;
* удалять свои stories.

На UI stories должны визуально отличаться от обычных posts.

---

# 17. CLUBS

Это одна из ключевых особенностей Bailanysta.

Club — это IT-сообщество внутри социальной сети.

Примеры:

* Python Kazakhstan;
* AI Engineers;
* Frontend Community;
* Cybersecurity;
* DevOps;
* Data Science;
* GameDev;
* Startups;
* Freelancers;
* JavaScript;
* Rust;
* Backend;
* Mobile Development.

Любой пользователь при наличии соответствующих прав может создать club.

---

# 18. CLUB STRUCTURE

Club должен быть больше, чем обычная страница.

Он должен напоминать Discord community.

Пример:

Python Kazakhstan

├── announcements
├── general
├── help
├── python
├── fastapi
├── ai
└── voice channels

Внутри клуба должны существовать:

* текстовые каналы;
* участники;
* роли/права доступа;
* сообщения;
* moderation capabilities.

В будущем возможны voice channels.

Но voice chat является сложной функцией.

Если дедлайн не позволяет качественно реализовать полноценный voice stack — НЕ ломай основной проект ради него.

Можно заложить архитектурное место для будущего voice functionality.

Качество основных функций важнее количества функций.

---

# 19. CLUB PERMISSIONS

Необходимо предусмотреть базовую модель прав:

* owner;
* admin/moderator;
* member.

Owner может:

* редактировать club;
* управлять участниками;
* управлять каналами;
* назначать moderators;
* удалять club.

Moderator может:

* модерировать сообщения;
* ограничивать пользователей;
* удалять нарушения.

Member может:

* писать в разрешённых каналах;
* читать;
* выходить из клуба.

Права должны проверяться на backend.

Нельзя доверять frontend authorization.

---

# 20. MESSAGING

Необходимо предусмотреть личные сообщения.

Минимум:

* conversation list;
* direct messages;
* отправка сообщений;
* получение сообщений;
* timestamps;
* read status;
* reactions;
* replies/edit/delete при наличии времени.

Архитектура должна позволять realtime messaging.

Предпочтительно использовать WebSocket для realtime-функций, если это не создаёт неоправданную сложность.

---

# 21. E2EE

Приватность является важным направлением проекта.

Однако НЕ жертвовать стабильностью MVP ради неподготовленной криптографии.

Для private messaging в перспективе должна быть возможность использовать end-to-end encryption.

Если E2EE будет реализовываться:

* использовать проверенные cryptographic libraries;
* не изобретать собственную криптографию;
* приватные ключи должны генерироваться/храниться на client side;
* сервер должен получать ciphertext, а не plaintext;
* сервер не должен иметь master decryption key;
* необходимо документировать модель угроз;
* необходимо документировать ограничения.

Нельзя писать маркетинговое заявление «100% anonymous» или «невозможно взломать».

Корректнее говорить:

> Privacy-focused architecture.

или

> End-to-end encrypted private messaging, если E2EE действительно реализован и проверен.

Если полноценное E2EE не успеваем реализовать качественно — лучше отложить его, чем реализовать криптографически сомнительное решение.

---

# 22. NOTIFICATIONS

Необходимо предусмотреть notification system.

Примеры:

* пользователь лайкнул пост;
* пользователь прокомментировал пост;
* кто-то подписался;
* пользователь был упомянут;
* активность в club;
* новое сообщение.

Notifications должны быть связаны с backend.

Для realtime notification можно использовать WebSocket/SSE при необходимости.

---

# 23. SEARCH

Необходим поиск.

Поиск должен позволять находить:

* users;
* posts;
* clubs;
* hashtags;
* projects.

На MVP достаточно PostgreSQL-based search, если он обеспечивает необходимую скорость.

Не нужно преждевременно подключать Elasticsearch/OpenSearch, если обычный PostgreSQL справляется.

---

# 24. PROJECTS

Пользователь может добавить проект в профиль.

Project может содержать:

* name;
* description;
* technologies;
* GitHub URL;
* demo URL;
* image;
* status.

Это НЕ заменяет GitHub.

Это showcase.

Пример:

AI Resume Analyzer

Python · FastAPI · React

GitHub
Live Demo

---

# 25. BOOKMARKS

Пользователь может сохранить пост.

Раздел:

Saved

где находятся сохранённые публикации.

---

# 26. DARK/LIGHT THEME

Обязательно реализовать:

* Light;
* Dark;
* возможно System.

Выбор темы должен сохраняться.

UI должен выглядеть хорошо в обеих темах.

Не должно быть компонентов, которые выглядят красиво только в light mode.

---

# 27. UI/UX

Это очень важно.

Проверяющий должен открыть сайт и сразу понять:

> «Это полноценный современный продукт».

Не использовать устаревший визуальный стиль.

Не делать всё в виде простых прямоугольных карточек с огромными рамками.

UI должен быть:

* современным;
* чистым;
* быстрым;
* responsive;
* accessible;
* consistent.

Предпочтительное направление:

modern social platform.

Можно вдохновляться современными паттернами Threads, Discord, Telegram, GitHub, но НЕ копировать их интерфейс напрямую.

---

# 28. RESPONSIVE

Приложение должно нормально работать:

* desktop;
* laptop;
* tablet;
* mobile.

На мобильном:

* sidebar может превращаться в bottom navigation;
* feed должен занимать доступную ширину;
* composer должен быть удобным;
* изображения не должны ломать layout;
* profile должен адаптироваться.

---

# 29. LOADING STATES

Обязательно использовать:

* skeletons;
* loaders;
* disabled states;
* empty states;
* error states.

Не должно быть ощущения, что сайт завис.

Например при загрузке feed:

показывать skeleton posts.

---

# 30. ACCESSIBILITY

Следовать базовым accessibility principles:

* semantic HTML;
* keyboard navigation;
* focus states;
* aria labels;
* readable contrast;
* buttons вместо div там, где это необходимо.

---

# 31. SECURITY

Безопасность должна учитываться с самого начала.

Минимально:

* password hashing;
* input validation;
* backend authorization;
* authentication;
* CORS configuration;
* rate limiting;
* SQL injection prevention через ORM/parameterized queries;
* XSS prevention;
* CSRF protection;
* secure cookies;
* security headers;
* upload validation;
* file size limits;
* MIME type validation;
* safe filename handling;
* environment secrets;
* no secrets in frontend bundle;
* no secrets in Git;
* backend permission checks;
* IDOR prevention;
* abuse protection.

Нельзя полагаться только на frontend validation.

Все критические проверки должны существовать на backend.

---

# 32. FILE UPLOAD SECURITY

Поскольку пользователи смогут загружать изображения и потенциально другие media files:

Необходимо:

* ограничивать размер;
* проверять MIME;
* проверять extension;
* генерировать безопасные имена;
* не доверять имени файла пользователя;
* по возможности перепроверять содержимое файла;
* ограничивать разрешённые форматы;
* не позволять произвольную загрузку исполняемых файлов;
* не хранить uploads в опасной директории.

---

# 33. API ARCHITECTURE

Frontend не должен напрямую обращаться к базе данных.

Архитектура:

Frontend
↓
Backend API
↓
Services
↓
Database / Storage / external services

Все внешние API должны вызываться с server side.

Это является обязательным требованием исходного задания.

Никакие secret API keys не должны попадать в browser.

---

# 34. API DESIGN

API должен быть логично структурирован.

Например:

/api/v1/auth

/api/v1/users

/api/v1/profiles

/api/v1/posts

/api/v1/comments

/api/v1/likes

/api/v1/follows

/api/v1/stories

/api/v1/clubs

/api/v1/messages

/api/v1/notifications

/api/v1/search

/api/v1/projects

/api/v1/bookmarks

Это только пример.

Можно выбрать другую структуру, если она архитектурно лучше.

---

# 35. BACKEND CODE QUALITY

Не создавать огромные файлы.

Использовать separation of concerns.

Предпочтительно:

backend/app/

├── main.py
├── core/
├── config/
├── database/
├── models/
├── schemas/
├── api/
├── services/
├── repositories/
├── middleware/
├── security/
└── tests/

Структура может быть изменена при необходимости.

---

# 36. FRONTEND CODE QUALITY

Не создавать гигантский App.tsx.

Предпочтительно разделить:

pages/

components/

features/

hooks/

lib/

services/

api/

layouts/

stores/

locales/

types/

и т.д.

Компоненты должны иметь одну понятную ответственность.

---

# 37. STATE MANAGEMENT

Не использовать глобальный state manager для всего подряд.

Разделять:

* server state;
* UI state;
* authentication state;
* local preferences.

TanStack Query можно использовать для server state.

Context/Zustand или аналог — только там, где действительно нужен client state.

---

# 38. PERFORMANCE

Приложение должно быть достаточно быстрым.

Не нужно преждевременно оптимизировать всё подряд.

Но необходимо:

* pagination;
* lazy loading;
* image optimization;
* предотвращение лишних API requests;
* правильное caching;
* database indexes;
* отсутствие N+1 queries;
* нормальная структура SQLAlchemy queries.

---

# 39. DATABASE INDEXES

Предусмотреть индексы для часто используемых запросов:

* username;
* email;
* created_at;
* post author;
* follows;
* hashtags;
* club members;
* messages;
* notifications.

Но индексы должны добавляться осмысленно.

---

# 40. TESTING

Проект должен иметь тесты.

Backend:

* authentication;
* permissions;
* posts;
* comments;
* likes;
* follows;
* clubs;
* critical API endpoints.

Frontend:

* хотя бы основные critical flows, если время позволяет.

Особое внимание:

* unauthorized requests;
* forbidden access;
* invalid input;
* nonexistent resources;
* duplicate operations;
* ownership checks.

---

# 41. ERROR HANDLING

API должен возвращать нормальные HTTP status codes.

Например:

400 — invalid request

401 — unauthenticated

403 — forbidden

404 — not found

409 — conflict

422 — validation error

429 — rate limit

500 — internal error

Frontend должен красиво обрабатывать ошибки.

Не показывать пользователю сырые stack traces.

---

# 42. ENVIRONMENT CONFIGURATION

Создать:

.env.example

В нём перечислить необходимые переменные без секретных значений.

Например:

DATABASE_URL=

SECRET_KEY=

CORS_ORIGINS=

STORAGE_BUCKET=

STORAGE_ENDPOINT=

и т.д.

Production secrets должны задаваться через hosting provider.

---

# 43. DEPLOYMENT

Приложение должно быть рассчитано на реальный cloud deployment.

Frontend можно разместить на:

* Vercel;
* Netlify;
* другом подходящем hosting.

Backend:

* Render;
* Railway;
* Fly.io;
* собственный сервер;
* другой подходящий cloud provider.

Database:

* PostgreSQL-compatible managed service.

Перед финальным deployment необходимо проверить актуальные бесплатные тарифы выбранных сервисов.

Не предполагать, что free tier всегда существует.

---

# 44. README

README.md является обязательной частью проекта.

Он должен содержать:

## Project overview

Что такое Bailanysta.

## Features

Основные возможности.

## Tech stack

Почему выбран конкретный стек.

## Architecture

Как frontend, backend, database и storage взаимодействуют.

## Installation

Как запустить локально.

## Environment variables

Какие переменные нужны.

## Development

Как работать над проектом.

## Deployment

Как задеплоить.

## Design process

Как проектировалось приложение.

## Unique approaches

Какие интересные решения были использованы.

## Trade-offs

Какие компромиссы были приняты.

## Security

Какие меры безопасности реализованы.

## Known issues

Известные проблемы и ограничения.

## Future improvements

Что можно добавить в будущем.

README должен выглядеть как README настоящего open-source продукта, а не как формальный документ для проверки задания.

---

# 45. PROJECT DOCUMENTATION

В корне проекта необходимо поддерживать документацию.

Создай:

PROJECT_STATE.md

ARCHITECTURE.md

SECURITY.md

и при необходимости другие документы.

---

# 46. PROJECT_STATE.md

Это очень важный файл.

Он используется как persistent memory проекта.

После каждого значимого этапа обновляй его.

Он должен содержать:

* текущий этап;
* завершённые этапы;
* текущую архитектуру;
* созданные features;
* изменённые файлы;
* database status;
* migrations;
* tests;
* known issues;
* deployment status;
* next step;
* технические решения;
* TODO.

Цель:

Если OpenCode будет перезапущен через несколько часов или дней, он сможет прочитать PROJECT_STATE.md и быстро восстановить контекст проекта.

---

# 47. ROOT PROMPT COPY

Сохрани этот MASTER PROMPT в проекте.

Например:

docs/MASTER_PROMPT.md

или:

MASTER_PROMPT.md

Выбери структуру, которая лучше соответствует проекту.

Главное — сохранить полный контекст.

Не удаляй этот документ.

---

# 48. WORKSPACE

Создай на Desktop отдельную папку проекта.

Название:

Bailanysta

Например:

Desktop/Bailanysta/

Внутри неё будет всё рабочее пространство:

Bailanysta/

├── frontend/
├── backend/
├── docs/
├── tests/
├── README.md
├── PROJECT_STATE.md
├── MASTER_PROMPT.md
├── ARCHITECTURE.md
├── SECURITY.md
├── .env.example
├── .gitignore
└── ...

Структуру можно изменить, если после архитектурного анализа будет более правильный вариант.

---

# 49. GIT

Инициализируй Git repository в проекте.

Создай качественный .gitignore.

НИКОГДА не добавляй:

.env

node_modules

**pycache**

.venv

build artifacts

IDE temporary files

local database files, если они не нужны для проекта.

Git history должна быть чистой и понятной.

---

# 50. DEVELOPMENT METHODOLOGY

Проект разрабатывается поэтапно.

НЕ нужно пытаться сделать всё за один шаг.

Каждый STEP должен:

1. Иметь конкретную цель.
2. Перед началом изучать текущее PROJECT_STATE.md.
3. Проверять существующую архитектуру.
4. Реализовывать только необходимые изменения.
5. Запускать соответствующие tests.
6. Исправлять найденные проблемы.
7. Проверять, что старые функции не сломались.
8. Обновлять PROJECT_STATE.md.
9. Обновлять README/документацию при необходимости.
10. В конце давать краткий отчёт:

* что сделано;
* какие файлы изменены;
* какие тесты запущены;
* какие проблемы остались;
* что рекомендуется делать следующим STEP.

---

# 51. НЕ ЛОМАЙ СУЩЕСТВУЮЩЕЕ

Это критически важно.

Если в будущем ты получишь STEP, не переписывай проект целиком.

Перед изменением:

* изучи существующий код;
* изучи PROJECT_STATE.md;
* пойми существующую архитектуру;
* переиспользуй существующие компоненты;
* не создавай дубликаты;
* не ломай API без причины;
* не удаляй рабочие функции без необходимости.

Если архитектурное изменение необходимо — объясни его.

---

# 52. НЕ СОЗДАВАЙ FAKE FUNCTIONALITY

Не делать кнопки, которые просто показывают:

"Coming soon"

если по заданию функция должна реально работать.

Не создавать mock data вместо реального backend там, где backend уже должен существовать.

Не создавать fake authentication.

Не делать fake likes.

Не делать fake profiles.

Не делать fake clubs.

Если функция заявлена как работающая — она должна быть подключена к реальному backend.

---

# 53. DEMO DATA

Для демонстрации можно предусмотреть seed data.

Например:

* несколько пользователей;
* несколько posts;
* несколько clubs;
* comments;
* likes.

Но seed data должна быть явно отделена от production user data.

Не хардкодить её непосредственно во frontend.

---

# 54. UX PRIORITY

При конфликте между количеством функций и качеством:

Качество важнее количества.

Лучше:

5 функций, которые работают идеально,

чем:

20 функций, из которых 15 сломаны.

---

# 55. TIME CONSTRAINT

Проект выполняется в очень жёсткий срок.

Целевой дедлайн:

06.09.2026, 23:59 по времени Алматы.

Поэтому при планировании:

PRIORITY 1:

* стабильное приложение;
* authentication;
* profiles;
* posts;
* feed;
* interactions;
* backend;
* database;
* deployment;
* responsive UI;
* three languages.

PRIORITY 2:

* clubs;
* stories;
* messaging;
* notifications;
* projects;
* search;
* bookmarks.

PRIORITY 3:

* advanced realtime;
* voice channels;
* E2EE;
* сложная recommendation system;
* дополнительные experimental features.

Если времени становится мало — сначала доведи PRIORITY 1 до стабильного состояния.

НЕ жертвуй базовой стабильностью ради второстепенной функции.

---

# 56. ПРОДУКТОВАЯ ФИЛОСОФИЯ

Bailanysta должна ощущаться как место, где IT-человеку хочется остаться.

Пользователь должен иметь возможность:

утром открыть ленту,

увидеть новости и посты коллег,

прочитать смешной IT-мем,

увидеть чей-то новый проект,

задать вопрос,

получить ответ,

зайти вечером в тематический клуб,

пообщаться,

и отправить человеку сообщение.

Это не только professional network.

И не только social network.

Это IT community platform.

---

# 57. DESIGN DIRECTION

Визуально:

Modern.

Minimal.

Premium.

Developer-oriented.

Но не стерильно.

Не делать интерфейс похожим на админ-панель.

Не делать огромные градиенты на каждом элементе.

Не использовать чрезмерное количество цветов.

Не превращать приложение в dashboard.

Основной UI должен быть ориентирован на контент и общение.

---

# 58. BRANDING

Название:

Bailanysta

Внутри интерфейса можно использовать короткое:

Bailanysta

Логотип должен быть простым и узнаваемым.

Не использовать чужие логотипы или trademark assets как собственный бренд.

---

# 59. NO AI ASSISTANT

Отдельно зафиксируй:

В текущей версии Bailanysta НЕ имеет встроенного AI writing assistant.

НЕ нужно реализовывать:

* AI генерацию постов;
* AI улучшение постов;
* AI генерацию кода;
* AI chat assistant;
* AI summaries.

Эти функции можно оставить в Future Roadmap.

Это сознательное product decision из-за сроков и фокуса на core social experience.

---

# 60. FUTURE ROADMAP

В README можно указать будущие возможности:

* AI-powered search;
* AI recommendations;
* AI moderation;
* advanced content discovery;
* voice/video channels;
* stronger E2EE architecture;
* mobile application;
* desktop application;
* advanced developer portfolio;
* job board;
* events;
* hackathons;
* integrations with GitHub/GitLab;
* developer reputation.

Но НЕ реализовывать их сейчас, если они не входят в текущий STEP.

---

# 61. CRITICAL RULE ABOUT EXTERNAL SERVICES

Все external APIs и внешние сервисы должны вызываться только с backend.

Frontend:

НЕ должен содержать private API keys.

НЕ должен напрямую вызывать secret external services.

Правильная схема:

Frontend
→ Backend
→ External API

Backend
→ Database

Backend
→ Storage

Backend
→ External services

---

# 62. BEFORE EVERY STEP

Перед каждым будущим STEP:

1. Прочитай PROJECT_STATE.md.
2. Прочитай relevant architecture docs.
3. Осмотри текущую структуру проекта.
4. Проверь существующие implementation.
5. Определи, что уже существует.
6. Только после этого начинай работу.

Не предполагай, что файл существует.

Не предполагай, что функция реализована.

Проверяй.

---

# 63. AFTER EVERY STEP

После завершения STEP:

1. Run tests.
2. Run lint/type checks.
3. Run build.
4. Проверить backend startup.
5. Проверить frontend startup/build.
6. Исправить очевидные ошибки.
7. Проверить affected functionality.
8. Обновить PROJECT_STATE.md.
9. Обновить документацию.
10. Сделать краткий итог.

Если что-то не удалось проверить — честно сообщить.

Не говорить "всё работает", если это не было проверено.

---

# 64. IMPORTANT ENGINEERING PRINCIPLE

Не усложняй проект ради красивых слов.

Если простое решение:

* надёжнее;
* быстрее;
* легче поддерживать;
* достаточно для MVP;

используй простое решение.

Но не жертвуй security и архитектурной целостностью.

---

# 65. FIRST ACTION

Сейчас НЕ реализуй полноценный функционал.

Сейчас выполни только подготовительный этап:

### STEP 0 — PROJECT INITIALIZATION

Сделай следующее:

1. Создай Desktop/Bailanysta.
2. Перейди в эту директорию.
3. Инициализируй Git.
4. Создай базовую структуру проекта.
5. Сохрани этот документ как MASTER_PROMPT.md.
6. Создай PROJECT_STATE.md.
7. Создай ARCHITECTURE.md.
8. Создай SECURITY.md.
9. Создай базовый README.md.
10. Создай .gitignore.
11. Создай .env.example.
12. Определи первоначальную архитектуру frontend/backend.
13. Зафиксируй архитектурные решения в ARCHITECTURE.md.
14. Зафиксируй security principles в SECURITY.md.
15. Зафиксируй состояние проекта в PROJECT_STATE.md.
16. НЕ начинай реализацию всех функций.
17. НЕ создавай огромный объём boilerplate без необходимости.

После этого:

* проверь структуру;
* проверь Git;
* убедись, что MASTER_PROMPT.md сохранён;
* убедись, что PROJECT_STATE.md содержит актуальный статус.

Затем остановись.

---

# 66. EXPECTED RESPONSE AFTER STEP 0

После выполнения STEP 0 ответь кратко:

* Workspace создан;
* MASTER_PROMPT сохранён;
* Architecture подготовлена;
* Security principles зафиксированы;
* Project State создан;
* Git initialized;
* проект готов к STEP 1.

После этого ЖДИ следующую команду.

Не начинай STEP 1 самостоятельно.

---

# 67. FINAL PRODUCT VISION

В конечном результате мы хотим получить:

## Bailanysta

A social platform for IT communities.

Пользователь открывает сайт.

Регистрируется.

Создаёт профиль.

Выбирает интересы.

Попадает в персональную ленту.

Публикует посты.

Ставит лайки.

Комментирует.

Подписывается.

Смотрит stories.

Находит клубы.

Вступает в клуб.

Общается в каналах.

Пишет личные сообщения.

Получает уведомления.

Ищет людей, посты и сообщества.

Добавляет проекты в профиль.

Переключает язык:

🇷🇺 Русский

🇰🇿 Қазақша

🇬🇧 English

Переключает тему:

☀️ Light

🌙 Dark

И всё это работает через реальный backend и database, а не через локальные mock-данные.

---

# 68. FINAL PRINCIPLE

Не пытайся сделать «самый большой проект».

Сделай:

**цельный, красивый, быстрый, понятный, безопасный и реально работающий продукт.**

Каждая функция должна иметь причину существовать.

Каждый технический выбор должен быть оправдан.

Каждый security-sensitive участок должен проверяться.

Каждый STEP должен оставлять проект в рабочем состоянии.

Если есть сомнение между:

"быстро сделать много"

и

"качественно сделать главное"

выбирай второе.

---

# END OF MASTER PROMPT

После выполнения STEP 0 остановись и жди дальнейшего указания.
