# 🧠 Meta — Документация системы агентов

**Назначение:** Эта папка содержит документацию о **работе над системой агентов**, а не о проекте kk-userator.

---

## 📁 Структура

| Файл | Описание |
|------|----------|
| `README.md` | Этот файл — навигация по документации |
| `git-workflow.md` | Git-воркфлоу (GitHub Flow) с лучшими практиками |
| `topics.md` | Список тем и областей знаний для системы |
| `multi-agent-patterns.md` | Паттерны проектирования мульти-агентных систем |
| `code-review-guidelines.md` | Руководство по код-ревью для агентов |
| `system-prompts.md` | Коллекция системных промптов и их версий |
| `roles-agents.md` | Роли, агенты, их обязанности и взаимодействия |

---

## 🎯 Для чего эта папка

**Проект (корень):**
- Код генератора пользователей Keycloak
- Скрипты, зависимости, документация для пользователя

**Meta (эта папка):**
- Как работает система агентов
- Лучшие практики, соглашения, принципы
- Эволюция промптов и архитектуры
- Уроки, инсайты, исправления ошибок

---

## 🔧 Использование

При изменении архитектуры системы агентов:
1. Обнови соответствующий файл в `meta/`
2. Закоммить с префиксом `meta:`
3. В activity.log укажи ссылку на изменённый файл

**Пример:**
```
[2026-03-19 01:20:46] [TRUSTED] START coordinator: "Создание meta/ — фундаментальная документация"
[2026-03-19 01:30:00] [TRUSTED] COMPLETE coordinator: "Созданы: git-workflow.md, topics.md, multi-agent-patterns.md"
```

---

## 📚 Источники

Документация основана на:
- [GitHub Docs — About branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
- [GitLab Code Review Guidelines](https://docs.gitlab.com/development/code_review/)
- [Six Core Design Principles for Multi-AI Agent Systems](https://cobusgreyling.substack.com/p/six-core-design-principles-for-multi)
- [Designing LLM Systems: Start Simple](https://medium.com/@Lokesh-Avlasia/designing-llm-systems-start-simple-with-the-right-architecture-424f965a3b24)

---

*Последнее обновление: 2026-03-19*
