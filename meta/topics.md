# 📚 Topics — Области знаний системы агентов

**Назначение:** Этот файл содержит список тем, которые могут понадобиться для работы системы агентов.

---

## 🏗️ Архитектура и дизайн

### Системная архитектура
- [ ] Многоуровневая архитектура (Layered Architecture)
- [ ] Микросервисы vs Монолит
- [ ] Event-driven архитектура
- [ ] CQRS (Command Query Responsibility Segregation)
- [ ] Domain-Driven Design (DDD)

### Паттерны проектирования
- [ ] GoF паттерны (Gang of Four)
- [ ] Enterprise Integration Patterns
- [ ] Architectural Decision Records (ADR)
- [ ] SOLID принципы
- [ ] DRY, KISS, YAGNI

---

## 🤖 Мульти-агентные системы

### Паттерны агентов
- [x] Flow Control (явный vs динамический)
- [x] Interaction Styles (handoff vs tool flow)
- [x] History Sharing (полный след vs только результаты)
- [x] Network Configurations (супервизор, рой, иерархия, SIE)
- [x] Human Interaction (in-the-loop vs on-the-loop)
- [x] ReAct Workflow (thought → action → observation)

### Специализация агентов
- [ ] Analyst — анализ требований
- [ ] Architect — системная архитектура
- [ ] Engineer — реализация кода
- [ ] Reviewer — код-ревью
- [ ] Planner — планирование
- [ ] Documenter — документирование
- [ ] Coordinator — оркестрация
- [ ] Orchestrator — сложные задачи

### Координация агентов
- [ ] Протоколы коммуникации
- [ ] Разделение контекста
- [ ] Артефакт-ориентированный подход
- [ ] Итеративные циклы
- [ ] Эскалация проблем

---

## 📝 Код-ревью

### Процессы ревью
- [x] Pull Request workflow
- [x] Чеклисты для ревьюера
- [x] Чеклисты для автора
- [ ] Статусы: Approved / Request Changes / Comment
- [ ] Обязательное ревью перед мержем

### Технические аспекты
- [ ] Статический анализ кода
- [ ] Линтеры и форматтеры
- [ ] Проверка зависимостей
- [ ] Безопасность (SAST, DAST)
- [ ] Производительность

### Коммуникация
- [ ] Конструктивная обратная связь
- [ ] Управление конфликтами
- [ ] Тайм-менеджмент ревью
- [ ] Асинхронное ревью

---

## 🔧 Разработка

### Языки программирования
- [ ] Python (основной)
- [ ] JavaScript/TypeScript
- [ ] Go
- [ ] Rust
- [ ] Java/Kotlin

### Фреймворки
- [ ] FastAPI / Django (Python backend)
- [ ] React / Vue (frontend)
- [ ] Node.js / Express (JS backend)
- [ ] pytest / unittest (тестирование)

### Инструменты
- [ ] Git (version control)
- [ ] Docker (контейнеризация)
- [ ] Kubernetes (оркестрация)
- [ ] CI/CD (GitHub Actions, GitLab CI)
- [ ] Pre-commit hooks

---

## 🗄️ Базы данных

### Реляционные
- [ ] PostgreSQL
- [ ] MySQL / MariaDB
- [ ] SQLite

### NoSQL
- [ ] MongoDB
- [ ] Redis
- [ ] Elasticsearch

### ORM и миграции
- [ ] SQLAlchemy
- [ ] Alembic
- [ ] Django ORM

---

## 🔐 Безопасность

### Аутентификация и авторизация
- [x] Keycloak (IAM)
- [ ] OAuth2 / OIDC
- [ ] JWT токены
- [ ] RBAC / ABAC

### Практики безопасности
- [ ] OWASP Top 10
- [ ] Secure coding guidelines
- [ ] Secrets management
- [ ] Audit logging

---

## 📦 Инфраструктура

### Облачные платформы
- [ ] AWS
- [ ] Azure
- [ ] Google Cloud
- [ ] Yandex Cloud

### Мониторинг и логирование
- [ ] Prometheus + Grafana
- [ ] ELK Stack (Elasticsearch, Logstash, Kibana)
- [ ] Sentry
- [ ] Distributed tracing (Jaeger, Zipkin)

### Сетевые технологии
- [ ] Nginx / Apache
- [ ] Load balancers
- [ ] CDN
- [ ] Service mesh (Istio)

---

## 📊 Качество кода

### Метрики
- [ ] Cyclomatic complexity
- [ ] Code coverage
- [ ] Technical debt ratio
- [ ] Maintainability index

### Инструменты
- [ ] SonarQube
- [ ] CodeClimate
- [ ] Lint (pylint, eslint)
- [ ] Black / Prettier (форматтеры)

---

## 🧪 Тестирование

### Уровни тестирования
- [ ] Unit тесты
- [ ] Integration тесты
- [ ] E2E тесты
- [ ] Load тесты

### Практики
- [ ] TDD (Test-Driven Development)
- [ ] BDD (Behavior-Driven Development)
- [ ] Mocking и stubbing
- [ ] Test fixtures

---

## 📖 Документация

### Типы документации
- [ ] README
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture Decision Records (ADR)
- [ ] Changelog
- [ ] Runbooks

### Инструменты
- [ ] Markdown
- [ ] MkDocs / Docusaurus
- [ ] Sphinx
- [ ] Mermaid (диаграммы)

---

## 🎯 Управление проектами

### Методологии
- [ ] Agile / Scrum
- [ ] Kanban
- [ ] Waterfall
- [ ] Lean

### Практики
- [ ] User stories
- [ ] MoSCoW приоритизация
- [ ] Definition of Done (DoD)
- [ ] Sprint planning / retrospective

### Трекинг
- [ ] GitHub Issues
- [ ] Jira
- [ ] Trello
- [ ] Notion

---

## 🧠 LLM и AI

### Архитектуры
- [ ] Transformer
- [ ] RAG (Retrieval-Augmented Generation)
- [ ] Fine-tuning vs Prompt engineering
- [ ] Function calling

### Практики
- [ ] Prompt engineering
- [ ] Chain of Thought
- [ ] Few-shot learning
- [ ] System prompts design

### Ограничения
- [ ] Hallucinations
- [ ] Context window limits
- [ ] Token costs
- [ ] Latency

---

## 📈 Масштабирование

### Горизонтальное масштабирование
- [ ] Load balancing
- [ ] Sharding
- [ ] Replication
- [ ] Caching стратегии

### Вертикальное масштабирование
- [ ] Query optimization
- [ ] Indexing
- [ ] Connection pooling

---

## ✅ Статусы

| Статус | Значение |
|--------|----------|
| `[ ]` | Не начато |
| `[/]` | В процессе |
| `[x]` | Завершено / Есть документация |

---

*Последнее обновление: 2026-03-19*
