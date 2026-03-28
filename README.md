# Keycloak User Generator

Пакет для массового создания пользователей в Keycloak через Admin API.

**Версия:** 2.0.0

**Статус:** Готов к использованию

**Лицензия:** MIT

---

## Описание

Инструмент предназначен для автоматизированного создания учётных записей в Keycloak через Admin API. Поддерживает конфигурацию через YAML-файлы и переменные окружения, идемпотентное создание пользователей и экспорт учётных данных в различных форматах.

**Основные возможности:**
- Массовое создание пользователей (от 1 до N за один запуск)
- Генерация безопасных паролей (настраиваемая длина и символы)
- Экспорт в CSV, TXT, JSON
- Идемпотентность (повторный запуск не создаёт дубликаты)
- Режим сухой проверки (dry-run)
- Валидация конфигурации
- Поддержка переменных окружения

---

## Требования

- Python 3.12 или выше
- Доступ к Keycloak Admin API
- Учётная запись администратора Keycloak с правами на создание пользователей

---

## Установка

### Вариант 1: Установка из PyPI

```bash
pip install kk-userator
```

### Вариант 2: Установка из исходников

```bash
# Клонирование репозитория
git clone <repository-url>
cd kk-userator

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Установка как пакета
pip install -e .
```

### Вариант 3: Режим разработки

```bash
# Установка с dev-зависимостями
pip install -e ".[dev]"

# Запуск тестов
pytest

# Линтинг
ruff check keycloak_userator/

# Проверка типов
mypy keycloak_userator/
```

**Зависимости:**
- `python-keycloak` ≥3.0.0 — Keycloak Admin API
- `python-dotenv` ≥1.0.0 — Загрузка .env файлов
- `PyYAML` ≥6.0 — YAML конфигурация
- `pytest` ≥7.0 — Тестирование (dev)
- `ruff` ≥0.1.0 — Линтинг (dev)
- `mypy` ≥1.0.0 — Проверка типов (dev)
- `bandit` ≥1.7.0 — Проверка безопасности (dev)

---

## Настройка

### 1. Переменные окружения (.env)

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```bash
# URL сервера Keycloak
KEYCLOAK_URL=https://keycloak.example.com

# Учётные данные администратора
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=your_password_here

# Realm (опционально, по умолчанию: master)
KEYCLOAK_REALM=master

# Префикс для логинов (опционально)
KEYCLOAK_LOGIN_PREFIX=user

# Домен для email (опционально)
KEYCLOAK_EMAIL_DOMAIN=example.com

# Количество пользователей (опционально)
KEYCLOAK_COUNT=100
```

### 2. Конфигурация (config.yaml)

```yaml
# Параметры пользователей
user:
  login_prefix: "user"              # Префикс для логинов
  email_domain: "example.com"       # Домен для email
  first_name: "User"                # Имя по умолчанию
  last_name_template: "User {number}"  # Шаблон фамилии
  group_name: "default-users"       # Группа в Keycloak
  default_realm: "master"           # Realm по умолчанию

# Параметры генерации паролей
password:
  length: 12                        # Длина пароля
  use_lowercase: true               # Строчные буквы
  use_uppercase: true               # Заглавные буквы
  use_digits: true                  # Цифры
  use_special: false                # Спецсимволы

# Параметры по умолчанию
defaults:
  count: 100                        # Количество пользователей
  start_number: 1                   # Начальный номер
  output_dir: "output"              # Директория для файлов

# Логирование
logging:
  file: "keycloak_generator.log"
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

---

## Использование

### Базовый запуск

```bash
# Неинтерактивный режим (переменные окружения, по умолчанию)
python -m keycloak_userator.cli

# Интерактивный режим (запросит данные для подключения)
python -m keycloak_userator.cli --interactive
```

### Параметры командной строки

```bash
python -m keycloak_userator.cli [OPTIONS]

Options:
  --count, -n INTEGER     Количество пользователей (по умолчанию: 100)
  --start, -s INTEGER     Начальный номер (по умолчанию: 1)
  --dry-run               Режим проверки (без создания)
  --output-dir, -o PATH   Директория для файлов
  --interactive, -i       Интерактивный режим (запрос данных)
  --config, -c PATH       Путь к config.yaml
  --help                  Показать справку
```

### Примеры

```bash
# Создать 50 пользователей
python -m keycloak_userator.cli --count 50

# Создать с 101 по 200
python -m keycloak_userator.cli --count 100 --start 101

# Режим проверки (dry-run)
python -m keycloak_userator.cli --dry-run --count 10

# Интерактивный режим
python -m keycloak_userator.cli --interactive

# Альтернативная конфигурация
python -m keycloak_userator.cli --config configs/another_project.yaml
```

---

## Форматы выходных файлов

После выполнения в директории `output/` создаются файлы:

| Файл | Формат | Назначение |
|------|--------|------------|
| `credentials_*.csv` | CSV | Импорт в другие системы |
| `credentials_*.txt` | TXT | Человекочитаемый формат |
| `credentials_*.json` | JSON | Программная обработка |

**Пример CSV:**
```csv
username,password,email,firstName,lastName,enabled
user_1,A7k2Bm9p,user_1@example.com,User,User 1,True
user_2,X3mN9qR2,user_2@example.com,User,User 2,True
```

---

## Интеграция

### OpenEDX / Moodle / Другие LMS

После создания пользователей в Keycloak:

1. Пользователь переходит на сайт LMS
2. Нажимает «Войти через Keycloak» (SSO)
3. Keycloak аутентифицирует пользователя
4. LMS автоматически создаёт локальную учётную запись
5. Пользователь получает доступ к курсу

**Дополнительная настройка не требуется!**

---

## Безопасность

### Хранение учётных данных

**Рекомендации:**
- Не храните файлы с паролями в открытом виде
- Используйте шифрование при передаче
- Удаляйте файлы после передачи пользователям
- Ограничивайте доступ к файлам (`chmod 600`)

### Переменные окружения

**Не коммитьте `.env` в git!** Файл уже в `.gitignore`.

```bash
# Ограничение доступа (Linux)
chmod 600 .env

# Проверка
ls -l .env
# -rw------- 1 user user ... .env
```

---

## Тестирование

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=keycloak_userator --cov-report=html

# Конкретный модуль
pytest tests/test_password.py -v
```

**Покрытие кода:** 92%+

---

## Статический анализ

```bash
# Линтинг
ruff check keycloak_userator/

# Проверка типов
mypy keycloak_userator/

# Безопасность
bandit -r keycloak_userator/
```

---

## Структура проекта

```
kk-userator/
├── keycloak_userator/       # Пакет
│   ├── __init__.py          # Экспорт классов
│   ├── cli.py               # Точка входа
│   ├── config.py            # Конфигурация
│   ├── types.py             # Типы данных
│   ├── password.py          # Генератор паролей
│   ├── exporter.py          # Экспорт данных
│   └── keycloak_client.py   # Keycloak API
├── tests/                   # Тесты
├── docs/                    # Документация
├── pyproject.toml           # Конфигурация сборки
├── README.md                # Этот файл
└── CHANGELOG.md             # История версий
```

---

## Обработка ошибок

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `401 Unauthorized` | Неверные учётные данные | Проверить логин/пароль |
| `403 Forbidden` | Недостаточно прав | Требуется роль `realm-management` |
| `ConnectionError` | Keycloak недоступен | Проверить сеть, URL |
| `ValidationError` | Ошибка в config.yaml | Проверить синтаксис YAML |

---

## Changelog

См. [CHANGELOG.md](CHANGELOG.md)

---

## Лицензия

MIT License — см. [LICENSE](LICENSE) файл.

---

## Поддержка

- Документация: `docs/`
- Issues: GitHub repository
- Email: разработчику

---

*Версия: 2.0.0*
*Дата: 2026-03-28*
