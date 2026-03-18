# 🌿 Git Workflow — GitHub Flow

**Источник:** [GitHub Docs — About branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)

---

## 📋 Обзор

**GitHub Flow** — это легковесный, ветка-ориентированный воркфлоу, разработанный для непрерывной доставки и частых развёртываний.

**Ключевые принципы:**
- ✅ Ветки изолируют изменения
- ✅ Короткоживущие feature-ветки
- ✅ Pull Request как точка ревью
- ✅ Мерж после одобрения
- ✅ Удаление ветки после мержа

---

## 🔄 Рабочий процесс

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Flow                              │
└─────────────────────────────────────────────────────────────────┘

     main (production-ready)
       │
       ├──────────────────────────────────────────────────────┐
       │                                                      │
       ▼                                                      │
  [1] Создать ветку                                           │
       │                                                      │
       ▼                                                      │
  [2] Делать коммиты                                          │
       │                                                      │
       ▼                                                      │
  [3] Открыть Pull Request                                    │
       │                                                      │
       ▼                                                      │
  [4] Code Review                                             │
       │                                                      │
       ├─────► [5a] Замечания ─────► Исправить ─────┐         │
       │                                            │         │
       ▼                                            │         │
  [5b] Одобрено                                     │         │
       │                                            │         │
       ▼                                            │         │
  [6] Мерж в main                                   │         │
       │                                            │         │
       ▼                                            │         │
  [7] Удалить ветку ◄───────────────────────────────┘         │
                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📝 Этапы подробно

### 1. Создать ветку

```bash
git checkout main
git pull origin main
git checkout -b feature/short-description
```

**Соглашения об именовании:**
| Префикс | Назначение | Пример |
|---------|------------|--------|
| `feature/` | Новая функциональность | `feature/user-auth` |
| `fix/` | Исправление бага | `fix/login-error` |
| `docs/` | Обновление документации | `docs/readme-update` |
| `refactor/` | Рефакторинг | `refactor/auth-module` |
| `test/` | Добавление тестов | `test/user-api` |
| `chore/` | Вспомогательные изменения | `chore/update-deps` |

**Правила:**
- Используйте `kebab-case` (через дефис)
- Краткое описание (2-4 слова)
- Избегайте специальных символов

---

### 2. Делать коммиты

```bash
git add .
git commit -m "type: описание"
git push origin feature/short-description
```

**Соглашения коммитов (Conventional Commits):**
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | Назначение |
|------|------------|
| `feat` | Новая функциональность |
| `fix` | Исправление бага |
| `docs` | Документация |
| `style` | Форматирование |
| `refactor` | Рефакторинг |
| `test` | Тесты |
| `chore` | Вспомогательное |

**Пример:**
```
feat(auth): добавить OAuth2 авторизацию

- Интеграция с Google OAuth
- Обработка токенов
- Обновление README

Closes #123
```

---

### 3. Открыть Pull Request

**Создание PR:**
```bash
# Через GitHub CLI
gh pr create --title "feat: добавить OAuth2" --body "Описание изменений"

# Или через GitHub UI: github.com/<owner>/<repo>/pull/new/branch
```

**Шаблон описания PR:**
```markdown
## Что сделано
- [ ] Описание изменений

## Зачем
- [ ] Проблема/задача

## Как тестировать
- [ ] Шаги для проверки

## Чеклист
- [ ] Код отформатирован
- [ ] Тесты проходят
- [ ] Документация обновлена
```

---

### 4. Code Review

**Для автора PR:**
- ✅ Запроси ревью явно (@reviewer)
- ✅ Ответь на все комментарии
- ✅ Внеси исправления до мержа
- ✅ Обновляй PR по замечаниям

**Для ревьюера:**
- ✅ Проверь соответствие требованиям
- ✅ Оставь конструктивные комментарии
- ✅ Используй [Approve / Request Changes / Comment]
- ✅ Проверь тесты и документацию

**Чеклист ревью:**
```markdown
## Код
- [ ] Логика корректна
- [ ] Нет дублирования
- [ ] Обработка ошибок
- [ ] Тесты покрывают изменения

## Безопасность
- [ ] Нет уязвимостей
- [ ] Валидация входных данных
- [ ] Нет секретов в коде

## Документация
- [ ] README обновлён
- [ ] Комментарии в коде
- [ ] Changelog обновлён
```

---

### 5. Мерж

**Требования перед мержем:**
- ✅ Все статус-чеки пройдены (CI/CD)
- ✅ Получено одобрение (1+ reviewer)
- ✅ Нет конфликтов слияния
- ✅ Чеклист ревью заполнен

**Способы мержа:**
| Метод | Когда использовать |
|-------|-------------------|
| **Squash and merge** | Feature-ветка с множеством коммитов |
| **Merge commit** | Сохранить историю ветки |
| **Rebase and merge** | Линейная история (для мелких изменений) |

**После мержа:**
```bash
git checkout main
git pull origin main
git branch -d feature/short-description  # Удалить локальную
git push origin --delete feature/short-description  # Удалить удалённую
```

---

### 6. Удаление ветки

**Важно:**
- ❌ Нельзя удалить ветку с открытым PR
- ✅ GitHub предлагает удалить после мержа
- ✅ Зависимые PR автоматически обновляются

---

## 🛡️ Защищённые ветки (Protected Branches)

**Настройки защиты для `main`:**
```
✅ Require a pull request before merging
✅ Require approvals (1 reviewer minimum)
✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging
✅ Include administrators (применяется ко всем)
```

**Дополнительно:**
- ✅ Require signed commits
- ✅ Require linear history
- ✅ Allow force pushes (только для администраторов)
- ✅ Allow deletions (не рекомендуется для main)

---

## 📊 Метрики воркфлоу

| Метрика | Цель |
|---------|------|
| Время жизни ветки | < 3 дней |
| Время ревью | < 24 часов |
| Размер PR | < 400 строк изменений |
| Количество коммитов в PR | 1-10 (после squash) |
| Конфликты слияния | < 5% PR |

---

## ⚠️ Частые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Долгоживущие ветки (>1 недели) | Конфликты, устаревание | Дробить на мелкие PR |
| Огромные PR (>1000 строк) | Долгое ревью, пропуск багов | Делить на логические части |
| Мерж без ревью | Баги в production | Включить защиту ветки |
| Force push в shared branch | Потеря коммитов коллег | Запретить force push |
| Игнорирование CI | Непрошедшие тесты | Требовать статус-чеки |

---

## 🔗 Ссылки

- [GitHub Docs — About branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
- [GitHub Flow — Official Guide](https://docs.github.com/en/get-started/using-github/github-flow)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitLab Code Review Guidelines](https://docs.gitlab.com/development/code_review/)

---

*Документ создан: 2026-03-19*
*Основано на: GitHub Docs, GitLab Handbook*
