# kk-userator — Контекст проекта

**Дата:** 2026-03-22  
**Версия:** 1.1.0 (с конфигурацией)  
**Тип:** Python-скрипт для массового создания пользователей в Keycloak

---

## 📋 Обзор проекта

**kk-userator** — утилита командной строки для автоматизированного создания учётных записей в Keycloak через Admin API. Предназначена для генерации пакет пользователей (по умолчанию 200) для курса «Английский для лиц с нарушениями зрения».

### Ключевые возможности

- ✅ Массовое создание пользователей через Keycloak Admin API
- ✅ Идемпотентность — повторный запуск не создаёт дубликаты
- ✅ Генерация безопасных паролей (настраиваемая длина и символы)
- ✅ Экспорт в CSV, TXT, JSON
- ✅ Логирование всех операций
- ✅ Режим сухой проверки (`--dry-run`)
- ✅ **Конфигурация через YAML-файл** (без жёстко зашитых констант)
- ✅ **Валидация параметров** (префикс, домен, длина пароля)
- ✅ Поддержка переменных окружения

### Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.8+ |
| Keycloak API | python-keycloak ≥3.0.0 |
| Переменные окружения | python-dotenv ≥1.0.0 |
| YAML-конфигурация | PyYAML ≥6.0 |

---

## 🚀 Запуск и использование

### Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Интерактивный режим (скрипт запросит данные для подключения)
python keycloak_user_generator.py
```

### Конфигурация

Параметры вынесены в `config.yaml`. Приоритет (от высшего к низшему):
1. Аргументы командной строки
2. Переменные окружения
3. Файл `config.yaml`
4. Встроенные значения по умолчанию

| Переменная | Описание | Пример |
|------------|----------|--------|
| `KEYCLOAK_URL` | URL сервера Keycloak | `https://keycloak.urfu.online` |
| `KEYCLOAK_USERNAME` | Логин администратора | `admin` |
| `KEYCLOAK_PASSWORD` | Пароль администратора | `secret` |
| `KEYCLOAK_REALM` | Имя realm | `master` |
| `KEYCLOAK_CONFIG` | Путь к config.yaml | `config.yaml` |
| `KEYCLOAK_LOGIN_PREFIX` | Префикс для логинов | `enginc` |
| `KEYCLOAK_EMAIL_DOMAIN` | Домен для email | `urfu.online` |
| `KEYCLOAK_COUNT` | Количество пользователей | `200` |
| `KEYCLOAK_OUTPUT_DIR` | Директория для файлов | `output` |

### Параметры командной строки

```bash
python keycloak_user_generator.py [OPTIONS]

# Основные опции:
  --count, -n INT      Количество пользователей (из config.yaml: 200)
  --start, -s INT      Начальный номер нумерации (из config.yaml: 1)
  --dry-run            Режим проверки без реального создания
  --output-dir, -o STR Директория для файлов (из config.yaml: output)
  --no-interactive     Использовать переменные окружения
  --config STR         Путь к файлу конфигурации (config.yaml)
```

### Примеры

```bash
# Создать 50 пользователей (с 1 по 50)
python keycloak_user_generator.py --count 50

# Создать пользователей с 101 по 200
python keycloak_user_generator.py --count 100 --start 101

# Режим сухой проверки
python keycloak_user_generator.py --dry-run

# Использование переменных окружения
export KEYCLOAK_URL=https://keycloak.urfu.online
export KEYCLOAK_USERNAME=admin
export KEYCLOAK_PASSWORD=secret
python keycloak_user_generator.py --no-interactive

# Альтернативная конфигурация
python keycloak_user_generator.py --config configs/another_course.yaml

# Переопределение параметров через env
export KEYCLOAK_LOGIN_PREFIX=mycourse
export KEYCLOAK_EMAIL_DOMAIN=example.com
python keycloak_user_generator.py --no-interactive
```

### Валидация конфигурации

Скрипт проверяет параметры при запуске:

| Параметр | Проверка |
|----------|----------|
| `login_prefix` | Латиница, цифры, подчёркивание; начинается с буквы; ≤32 символов |
| `email_domain` | Не пустой; содержит точку; допустимые символы |
| `password.length` | 6–128 символов |
| `last_name_template` | Должен содержать `{number}` |
| `group_name` | Не пустой; ≤64 символов |

---

## 📁 Структура проекта

```
kk-userator/
├── keycloak_user_generator.py    # Основной скрипт (600+ строк)
├── config.py                     # Модуль конфигурации и валидации
├── config.yaml                   # Файл настроек (игнорируется git)
├── config.yaml.example           # Пример конфигурации
├── .env.example                  # Пример переменных окружения
├── requirements.txt              # Python-зависимости
├── README.md                     # Пользовательская документация
├── QWEN.md                       # Этот файл — контекст для ИИ-агента
├── AGENTS.md                     # Промпты субагентов (analyst, engineer, reviewer...)
├── docs/
│   └── requirements.md           # Техническое задание
├── meta/                         # Документация системы агентов
│   ├── README.md
│   └── docs/
│       ├── git-workflow.md
│       ├── code-review-guidelines.md
│       ├── multi-agent-patterns.md
│       └── ...
├── output/                       # Генерируемые файлы (игнорируются git)
│   ├── credentials_*.csv
│   ├── credentials_*.txt
│   └── credentials_*.json
└── keycloak_generator.log        # Лог операций (игнорируется git)
```

---

## 📊 Формат генерируемых данных

### Шаблон пользователей

| Поле | Формат | Пример |
|------|--------|--------|
| Логин | `enginc_{N}` | `enginc_1`, `enginc_2` |
| Пароль | 8 символов (a-zA-Z0-9) | `A7k2Bm9p` |
| Email | `enginc_{N}@urfu.online` | `enginc_1@urfu.online` |
| Имя | Статичное | `Студент` |
| Фамилия | `Студентов {N}` | `Студентов 1` |
| Группа | Статичная | `engforinclusb-users` |
| Статус | Enabled | `True` |

### Выходные файлы

После выполнения создаются в `output/`:

- `credentials_YYYYMMDD_HHMMSS.csv` — машиночитаемый формат
- `credentials_YYYYMMDD_HHMMSS.txt` — человекочитаемый формат
- `credentials_YYYYMMDD_HHMMSS.json` — для программной обработки

---

## 🔧 Разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск тестов

Тесты отсутствуют (на момент 2026-03-22). При добавлении функциональности рекомендуется создать `tests/`.

### Стиль кода

- **PEP 8** — базовое руководство
- **Type hints** — используются (`typing.Optional`, `typing.List`, `typing.Dict`)
- **Docstrings** — обязательны для классов и публичных методов
- **Логирование** — через `logging`, уровни: INFO (операции), DEBUG (детали), ERROR (ошибки)

### Архитектура кода

```
┌─────────────────────────────────────────────────────────┐
│                     main()                              │
│  ─────────────────────────────────────────────────────  │
│  1. create_argument_parser()  → args                   │
│  2. load_application_config() → Config                 │
│  3. get_credentials()         → credentials            │
│  4. KeycloakUserGenerator()   → generator              │
│  5. generator.connect()                                  │
│  6. generator.generate_users() → created_users         │
│  7. export_credentials()                                 │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│config.py      │ │Password       │ │Credential     │
│───────────────│ │Generator      │ │Exporter       │
│ConfigLoader   │ │───────────────│ │───────────────│
│Config         │ │• __init__(cfg)│ │• export_csv() │
│UserConfig     │ │• generate()   │ │• export_txt() │
│PasswordConfig │ │• generate_    │ │• export_json() │
│DefaultsConfig │ │  batch()      │ │               │
│LoggingConfig  │ │               │ │               │
│               │ │               │ │               │
│Валидаторы:    │ │               │ │               │
│• validate_    │ │               │ │               │
│  login_prefix │ │               │ │               │
│• validate_    │ │               │ │               │
│  email_domain │ │               │ │               │
│• validate_    │ │               │ │               │
│  password_    │ │               │ │               │
│  length       │ │               │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │Keycloak         │
                 │UserGenerator    │
                 │─────────────────│
                 │• connect()      │
                 │• generate_      │
                 │  users()        │
                 │• _create_user() │
                 │• _user_exists() │
                 │• _generate_user_│
                 │  data()         │
                 └─────────────────┘
```

---

## 🔒 Безопасность

### Критичные правила

1. **Не хранить пароли администратора в коде** — использовать `input()` или переменные окружения
2. **Защищать файлы с учётными данными** — `chmod 700 output/`
3. **Использовать HTTPS** — не запускать с публичных Wi-Fi без VPN
4. **Удалять файлы после передачи** — `rm -rf output/` или архивировать с паролем

### `.gitignore` защищает

```
credentials_*.csv
credentials_*.txt
credentials_*.json
keycloak_generator.log
output/
```

---

## 🧩 Система субагентов (AGENTS.md)

Проект использует **мульти-агентный паттерн** для разработки:

| Роль | Обязанность | Артефакт |
|------|-------------|----------|
| **analyst** | Анализ требований | `docs/requirements.md` |
| **architect** | Проектирование архитектуры | `docs/architecture.md` |
| **planner** | Планирование работ | `docs/plan.md` |
| **engineer** | Реализация кода | `src/`, `tests/` |
| **reviewer** | Код-ревью, проверка зависимостей | `reviews/*.md` |
| **documenter** | Документация | `README.md`, `docs/*.md` |
| **orchestrator** | Координация сложных задач | `docs/orchestration-*.md` |

### Режимы работы

- **🚀 Fast Path** (<2 часов) → `engineer → reviewer → Done`
- **🏗️ Full Path** (крупные задачи) → `analyst → reviewer → architect → reviewer → planner → engineer → reviewer → Done`
- **🎼 Orchestrator** (>3 подзадач) → декомпозиция + синтез

### Журналирование (activity.log)

Все события записываются в `docs/activity.log`:

```
[YYYY-MM-DD HH:MM:SS] [TRUSTED/UNTRUSTED] <ТИП> <СУБЪЕКТ>: <описание>
```

---

## 📝 Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.1.0 | 2026-03-22 | Конфигурация в YAML, валидация параметров, декомпозиция main() |
| 1.0.0 | 2026-03-18 | Базовая версия: генерация 200 пользователей, экспорт CSV/TXT/JSON |

---

## 🆘 Обработка ошибок

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `KeycloakError: 401 Unauthorized` | Неверные учётные данные | Проверить логин/пароль администратора |
| `KeycloakError: 403 Forbidden` | Недостаточно прав | Требуется роль `realm-admin` |
| `ConnectionError` | Keycloak недоступен | Проверить сетевое подключение |
| `ImportError: python-keycloak` | Не установлены зависимости | `pip install -r requirements.txt` |

---

## 📚 Ссылки

- [Keycloak Admin API Documentation](https://www.keycloak.org/docs-api/latest/rest-api/)
- [python-keycloak (PyPI)](https://pypi.org/project/python-keycloak/)
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)

---

*QWEN.md создан: 2026-03-22*  
*Для обновления: добавить новые разделы по мере развития проекта*
