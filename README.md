# Keycloak User Generator

Пакет для массового создания пользователей в Keycloak через Admin API.

Предназначен для генерации учётных записей для курса **«Английский для лиц с нарушениями зрения»**.

**Версия:** 2.0.0 (рефакторинг в пакет)

**Статус:** ✅ Готов к использованию

---

## Требования

- Python 3.12 или выше
- Доступ к Keycloak Admin API
- Учётная запись администратора Keycloak с правами на создание пользователей

---

## Установка

### 1. Клонирование или загрузка

```bash
git clone <repository-url>
cd kk-userator
```

### 2. Создание виртуального окружения (рекомендуется)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

**Зависимости:**
- `python-keycloak` ≥3.0.0 — Keycloak Admin API
- `python-dotenv` ≥1.0.0 — Загрузка .env файлов
- `PyYAML` ≥6.0 — YAML конфигурация
- `pytest` ≥7.0 — Тестирование (включено в requirements.txt)

### 4. Настройка .env

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```bash
KEYCLOAK_URL=https://keycloak.urfu.online
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=your_password_here
KEYCLOAK_REALM=master
```

---

## Конфигурация

### Файл config.yaml

Все параметры вынесены в файл `config.yaml`. Это позволяет запускать скрипт для разных курсов без изменения кода.

```yaml
# Параметры пользователей
user:
  login_prefix: "enginc"           # Префикс для логинов
  email_domain: "urfu.online"      # Домен для email
  first_name: "Студент"            # Имя по умолчанию
  last_name_template: "Студентов {number}"  # Шаблон фамилии
  group_name: "engforinclusb-users"  # Группа в Keycloak
  default_realm: "master"          # Realm по умолчанию

# Параметры генерации паролей
password:
  length: 8                        # Длина пароля
  use_lowercase: true              # Строчные буквы
  use_uppercase: true              # Заглавные буквы
  use_digits: true                 # Цифры
  use_special: false               # Спецсимволы

# Параметры по умолчанию
defaults:
  count: 200                       # Количество пользователей
  start_number: 1                  # Начальный номер
  output_dir: "output"             # Директория для файлов

# Логирование
logging:
  file: "keycloak_generator.log"
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### Переменные окружения

Некоторые параметры можно переопределить через переменные окружения:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `KEYCLOAK_URL` | URL сервера Keycloak | `https://openedu.urfu.ru/auth` |
| `KEYCLOAK_USERNAME` | Логин администратора | `admin` |
| `KEYCLOAK_PASSWORD` | Пароль администратора | `secret` |
| `KEYCLOAK_REALM` | Имя realm | `master` |
| `KEYCLOAK_CONFIG` | Путь к config.yaml | `config.yaml` |
| `KEYCLOAK_LOGIN_PREFIX` | Префикс для логинов | `enginc` |
| `KEYCLOAK_EMAIL_DOMAIN` | Домен для email | `urfu.online` |
| `KEYCLOAK_COUNT` | Количество пользователей | `200` |
| `KEYCLOAK_OUTPUT_DIR` | Директория для файлов | `output` |

### Быстрая настройка для другого курса

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте `.env`:
   ```bash
   KEYCLOAK_URL=https://openedu.urfu.ru/auth
   KEYCLOAK_USERNAME=admin
   KEYCLOAK_PASSWORD=your_password
   ```

3. Отредактируйте `config.yaml` под ваш курс:
   ```yaml
   user:
     login_prefix: "mycourse"
     email_domain: "example.com"
     first_name: "Имя"
     last_name_template: "Фамилия {number}"
   ```

---

## Использование

### Быстрый старт (интерактивный режим)

```bash
python keycloak_user_generator.py
```

Скрипт запросит:
1. URL сервера Keycloak
2. Имя пользователя администратора
3. Пароль администратора
4. Имя realm (по умолчанию: `master`)

После подключения будет создано 200 пользователей с логинами `enginc_1` ... `enginc_200`.

---

### Параметры командной строки

| Параметр | Краткий | Описание | По умолчанию |
|----------|---------|----------|--------------|
| `--count` | `-n` | Количество пользователей | из config.yaml (200) |
| `--start` | `-s` | Начальный номер нумерации | из config.yaml (1) |
| `--dry-run` | — | Режим проверки без создания | выключен |
| `--output-dir` | `-o` | Директория для файлов | из config.yaml (`output`) |
| `--no-interactive` | — | Использовать переменные окружения | выключен |
| `--config` | — | Путь к файлу конфигурации | `config.yaml` |

Приоритет параметров (от высшего к низшему):
1. Аргументы командной строки
2. Переменные окружения
3. Файл `config.yaml`
4. Встроенные значения по умолчанию

---

### Примеры использования

#### Создать 50 пользователей (с 1 по 50)
```bash
python keycloak_user_generator.py --count 50
```

#### Создать пользователей с 101 по 200
```bash
python keycloak_user_generator.py --count 100 --start 101
```

#### Режим сухой проверки (без реального создания)
```bash
python keycloak_user_generator.py --dry-run
```

#### Использование переменных окружения
```bash
export KEYCLOAK_URL=https://keycloak.urfu.online
export KEYCLOAK_USERNAME=admin
export KEYCLOAK_PASSWORD=your_password
export KEYCLOAK_REALM=master

python keycloak_user_generator.py --no-interactive
```

#### Использование альтернативной конфигурации
```bash
python keycloak_user_generator.py --config configs/another_course.yaml
```

#### Переопределение параметров конфигурации
```bash
# Временное изменение префикса и домена
export KEYCLOAK_LOGIN_PREFIX=mycourse
export KEYCLOAK_EMAIL_DOMAIN=example.com
python keycloak_user_generator.py --no-interactive
```

---

## Формат генерируемых данных

### Логины
```
enginc_1, enginc_2, enginc_3, ..., enginc_200
```

### Пароли
- Длина: 8 символов
- Символы: латиница (строчные + заглавные) + цифры
- Пример: `A7k2Bm9p`

### Email
```
enginc_1@urfu.online, enginc_2@urfu.online, ..., enginc_200@urfu.online
```

### Имя и фамилия
- **Имя:** Студент
- **Фамилия:** Студентов N (где N — номер пользователя)

### Группа
Все пользователи добавляются в группу `engforinclusb-users`.

---

## Выходные файлы

После успешного выполнения в директории `output/` создаются:

| Файл | Формат | Описание |
|------|--------|----------|
| `credentials_YYYYMMDD_HHMMSS.csv` | CSV | Машиночитаемый формат |
| `credentials_YYYYMMDD_HHMMSS.txt` | TXT | Человекочитаемый формат |
| `credentials_YYYYMMDD_HHMMSS.json` | JSON | Для программной обработки |

### Пример CSV
```csv
username,password,email,firstName,lastName,enabled
enginc_1,A7k2Bm9p,enginc_1@urfu.online,Студент,Студентов 1,True
enginc_2,X3m9Kp2q,enginc_2@urfu.online,Студент,Студентов 2,True
```

### Пример TXT
```
================================================================================
УЧЁТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK
Дата генерации: 2026-03-18 15:30:45
Всего пользователей: 200
================================================================================

№ 1
  Логин:   enginc_1
  Пароль:  A7k2Bm9p
  Email:   enginc_1@urfu.online
  Имя:     Студент
  Фамилия: Студентов 1
  Статус:  Активен
----------------------------------------
```

---

## Валидация конфигурации

Скрипт автоматически проверяет корректность параметров:

| Параметр | Проверка |
|----------|----------|
| `login_prefix` | Только латиница, цифры, подчёркивание; начинается с буквы; макс. 32 символа |
| `email_domain` | Не пустой; содержит точку; допустимые символы |
| `password.length` | От 6 до 128 символов |
| `last_name_template` | Должен содержать `{number}` |
| `group_name` | Не пустой; макс. 64 символа |

При ошибке валидации скрипт завершится с описанием проблемы.

---

## Логирование

Все операции записываются в файл `keycloak_generator.log` в текущей директории.

Формат лога:
```
2026-03-18 15:30:45 - INFO - Подключение к Keycloak: https://keycloak.urfu.online
2026-03-18 15:30:46 - INFO - Успешное подключение к realm: master
2026-03-18 15:30:47 - INFO - Создание группы 'engforinclusb-users'
2026-03-18 15:30:48 - INFO - Создан: enginc_1 | enginc_1@urfu.online
```

---

## Идемпотентность

При повторном запуске скрипт **не создаёт дубликаты**:
- Если пользователь с таким логином уже существует — он пропускается
- В логе появляется запись: `Пользователь 'enginc_1' уже существует - пропускаем`
- В статистике увеличивается счётчик `skipped`

---

## Безопасность

### ⚠️ Важные предупреждения

1. **Не храните пароли администратора в коде**
   - Используйте интерактивный ввод или переменные окружения

2. **Защищайте файлы с учётными данными**
   - Файлы содержат пароли в открытом виде
   - Ограничьте доступ к директории `output/`
   - Передавайте файлы только авторизованным лицам

3. **Используйте HTTPS**
   - Убедитесь, что Keycloak доступен по HTTPS
   - Не используйте скрипт с публичных Wi-Fi без VPN

### Рекомендуемые меры

```bash
# Установить права доступа только для владельца
chmod 700 output/
chmod 600 output/*.csv output/*.txt output/*.json

# После передачи файлов — удалить или заархивировать с паролем
rm -rf output/
# или
zip -P secure_password credentials.zip output/*
rm -rf output/
```

---

## Обработка ошибок

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Ошибка подключения к Keycloak` | Неверный URL или нет сети | Проверьте URL и сетевое подключение |
| `KeycloakError: 401 Unauthorized` | Неверные логин/пароль | Проверьте учётные данные администратора |
| `KeycloakError: 403 Forbidden` | Недостаточно прав | Убедитесь, что пользователь имеет роль `realm-admin` |
| `ConnectionError` | Keycloak недоступен | Проверьте доступность сервера |

---

## Структура проекта

```
kk-userator/
├── keycloak_user_generator.py    # Основной скрипт
├── config.py                     # Модуль конфигурации и валидации
├── config.yaml                   # Файл настроек (параметры пользователей, паролей, логирования)
├── .env.example                  # Пример переменных окружения
├── requirements.txt              # Зависимости Python
├── README.md                     # Этот файл
├── output/                       # Директория с учётными данными (создаётся при запуске)
│   ├── credentials_*.csv
│   ├── credentials_*.txt
│   └── credentials_*.json
└── keycloak_generator.log        # Файл логов (создаётся при запуске)
```

---

## Интеграция с OpenEDX (Tutor)

После создания пользователей в Keycloak:

1. Учётные записи в OpenEDX создаются **автоматически** при первом входе
2. Пользователь входит через SSO (Keycloak)
3. При первом входе OpenEDX создаёт локальную учётную запись

### Проверка интеграции

1. Выберите 5 случайных пользователей из файла
2. Попробуйте войти через Keycloak в OpenEDX
3. Убедитесь, что учётная запись создаётся автоматически

---

## Поддержка

Вопросы и предложения направляйте через систему отслеживания задач проекта.

---

## Лицензия

Внутренний инструмент для проекта kk-userator.

---

*Версия: 2.0.0*
*Дата: 2026-03-28*

## Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| **2.0.0** | 2026-03-28 | **Рефакторинг в пакет**: модульная структура (cli, config, types, password, exporter, keycloak_client), 145 тестов (покрытие 93%+), .env поддержка (load_dotenv), ruff/mypy/bandit проверки |
| 1.1.0 | 2026-03-22 | Вынесена конфигурация в config.yaml, добавлена валидация параметров, декомпозиция main() |
| 1.0.0 | 2026-03-18 | Базовая версия: генерация 200 пользователей, экспорт CSV/TXT/JSON |
