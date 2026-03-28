# Руководство оператора

## 1. Введение

Это руководство предназначено для пользователей, которые будут:
- Запускать программу для создания пользователей
- Настраивать параметры генерации
- Обрабатывать результаты работы

**Требуемые знания:**
- Базовые навыки работы с командной строкой
- Понимание структуры файлов (CSV, TXT)
- Доступ к Keycloak (учётная запись администратора)

---

## 2. Быстрый старт

### 2.1. Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd kk-userator

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -e .
```

### 2.2. Настройка

```bash
# Копирование примера конфигурации
cp .env.example .env
cp config.yaml.example config.yaml

# Редактирование .env
nano .env  # или ваш редактор
```

**Заполните .env:**
```bash
KEYCLOAK_URL=https://keycloak.urfu.online
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=ваш_пароль
KEYCLOAK_REALM=master
```

### 2.3. Первый запуск

```bash
# Неинтерактивный режим (переменные окружения, по умолчанию)
python -m keycloak_userator.cli

# Интерактивный режим (запросит данные)
python -m keycloak_userator.cli --interactive

# Режим проверки (без создания)
python -m keycloak_userator.cli --dry-run --count 5
```

---

## 3. Конфигурация

### 3.1. Файл config.yaml

Откройте `config.yaml` в редакторе:

```yaml
user:
  login_prefix: "enginc"           # Префикс для логинов
  email_domain: "urfu.online"      # Домен для email
  first_name: "Студент"            # Имя
  last_name_template: "Студентов {number}"  # Фамилия
  group_name: "engforinclusb-users"  # Группа

defaults:
  count: 200                       # Количество
  start_number: 1                  # Начальный номер
```

**Изменение для другого курса:**

```yaml
user:
  login_prefix: "math2025"         # Новый префикс
  email_domain: "university.edu"   # Новый домен
  first_name: "Student"
  last_name_template: "User {number}"
  group_name: "math-course-users"

defaults:
  count: 150                       # Другое количество
```

### 3.2. Переменные окружения

**Создание .env файла:**

```bash
# Копирование примера
cp .env.example .env

# Редактирование
nano .env
```

**Содержимое .env:**
```bash
# URL Keycloak
KEYCLOAK_URL=https://keycloak.urfu.online

# Учётные данные администратора
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=secret_password

# Realm (опционально)
KEYCLOAK_REALM=master

# Переопределение параметров (опционально)
KEYCLOAK_LOGIN_PREFIX=enginc
KEYCLOAK_EMAIL_DOMAIN=urfu.online
KEYCLOAK_COUNT=200
```

**⚠️ Важно:** Не коммитьте `.env` в git! Файл уже в `.gitignore`.

### 3.3. Приоритет настроек

| Источник | Приоритет | Пример |
|----------|-----------|--------|
| Аргументы командной строки | 1 (высший) | `--count 50` |
| Переменные окружения | 2 | `KEYCLOAK_COUNT=50` |
| Файл config.yaml | 3 | `count: 50` |
| Значения по умолчанию | 4 (низший) | `200` |

---

## 4. Запуск программы

### 4.1. Основные режимы

#### Интерактивный режим

```bash
python -m keycloak_userator.cli
```

**Программа запросит:**
```
URL Keycloak (например, https://keycloak.urfu.online):
Имя пользователя администратора: admin
Пароль администратора: ********
Realm [master]:
```

#### Режим с переменными окружения

```bash
python -m keycloak_userator.cli
```

**Требует:**
- `KEYCLOAK_URL` — установлен
- `KEYCLOAK_USERNAME` — установлен
- `KEYCLOAK_PASSWORD` — установлен

#### Интерактивный режим

```bash
python -m keycloak_userator.cli --interactive
```

**Запросит:**
- URL Keycloak
- Имя пользователя администратора
- Пароль
- Realm (опционально)

#### Режим проверки (dry-run)

```bash
python -m keycloak_userator.cli --dry-run --count 5
```

**Вывод:**
```
[DRY-RUN] Будет создан: enginc_1 | enginc_1@urfu.online
[DRY-RUN] Будет создан: enginc_2 | enginc_2@urfu.online
...
```

**Реальные пользователи НЕ создаются!**

### 4.2. Параметры командной строки

| Параметр | Короткий | Описание | Пример |
|----------|----------|----------|--------|
| `--count` | `-n` | Количество пользователей | `--count 50` |
| `--start` | `-s` | Начальный номер | `--start 101` |
| `--dry-run` | | Режим проверки | `--dry-run` |
| `--output-dir` | `-o` | Директория вывода | `-o output` |
| `--interactive` | `-i` | Интерактивный режим | `--interactive` |
| `--config` | `-c` | Путь к config.yaml | `-c custom.yaml` |
| `--help` | `-h` | Справка | `--help` |

### 4.3. Примеры использования

**Создать 50 пользователей (с 1 по 50):**
```bash
python -m keycloak_userator.cli --count 50
```

**Создать 100 пользователей (с 101 по 200):**
```bash
python -m keycloak_userator.cli --count 100 --start 101
```

**Режим проверки:**
```bash
python -m keycloak_userator.cli --dry-run --count 10
```

**С переменными окружения:**
```bash
export KEYCLOAK_URL=https://keycloak.urfu.online
export KEYCLOAK_USERNAME=admin
export KEYCLOAK_PASSWORD=secret
python -m keycloak_userator.cli --no-interactive
```

**Альтернативная конфигурация:**
```bash
python -m keycloak_userator.cli --config configs/another_course.yaml
```

**Сохранение в другую директорию:**
```bash
python -m keycloak_userator.cli -o /path/to/output
```

---

## 5. Обработка результатов

### 5.1. Файлы с учётными данными

После успешного выполнения в директории `output/` создаются файлы:

```
output/
├── credentials_20260328_120000.csv
├── credentials_20260328_120000.txt
└── credentials_20260328_120000.json
```

**Формат имён:** `credentials_YYYYMMDD_HHMMSS.{format}`

### 5.2. Форматы файлов

#### CSV (машиночитаемый)

**Открытие:** Excel, Google Sheets, любой текстовый редактор

**Структура:**
```csv
username,password,email,firstName,lastName,enabled
enginc_1,A7k2Bm9p,enginc_1@urfu.online,Студент,Студентов 1,True
enginc_2,X3mN9qR2,enginc_2@urfu.online,Студент,Студентов 2,True
```

**Использование:**
- Импорт в другие системы
- Обработка скриптами
- Фильтрация в Excel

#### TXT (человекочитаемый)

**Открытие:** Любой текстовый редактор

**Структура:**
```
================================================================================
УЧЁТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK
Дата генерации: 2026-03-28 12:00:00
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

№ 2
  Логин:   enginc_2
  Пароль:  X3mN9qR2
  ...
```

**Использование:**
- Печать для передачи
- Отправка по email
- Чтение человеком

#### JSON (программная обработка)

**Открытие:** Текстовый редактор, JSON-вьюер

**Структура:**
```json
{
  "generated_at": "2026-03-28T12:00:00",
  "total_users": 200,
  "users": [
    {
      "username": "enginc_1",
      "password": "A7k2Bm9p",
      "email": "enginc_1@urfu.online",
      "firstName": "Студент",
      "lastName": "Студентов 1",
      "enabled": true
    }
  ]
}
```

**Использование:**
- Импорт в другие программы
- Автоматизация
- Интеграция по API

### 5.3. Передача учётных данных

**⚠️ Безопасность:**

1. **Не отправляйте пароли в открытом виде!**
2. **Заархивируйте файл с паролем**
3. **Передавайте пароль от архива отдельно**

**Рекомендуемый процесс:**

```bash
# Создание зашифрованного архива (Linux)
zip -e credentials.zip credentials_*.txt

# Отправка архива
# ... по почте / файлообменнику

# Пароль от архива
# ... по телефону / в другом канале
```

---

## 6. Интеграция с OpenEDX

### 6.1. Автоматическое создание

После создания пользователей в Keycloak:

1. Пользователь переходит на сайт курса OpenEDX
2. Нажимает «Войти через Keycloak» (SSO)
3. Keycloak аутентифицирует пользователя
4. OpenEDX автоматически создаёт локальную учётную запись
5. Пользователь получает доступ к курсу

**Ничего дополнительно делать не нужно!**

### 6.2. Проверка интеграции

**Шаг 1:** Выберите 3-5 случайных пользователей из файла

**Шаг 2:** Попробуйте войти под каждым:
- Откройте сайт OpenEDX
- Нажмите «Войти»
- Введите логин и пароль из файла
- Проверьте доступ к курсу

**Шаг 3:** Если вход не удался:
- Проверьте URL Keycloak в настройках OpenEDX
- Проверьте права доступа в Keycloak
- Проверьте логи OpenEDX

---

## 7. Обработка ошибок

### 7.1. Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `401 Unauthorized` | Неверный логин/пароль | Проверьте KEYCLOAK_USERNAME/PASSWORD |
| `403 Forbidden` | Недостаточно прав | Требуется роль `realm-management` |
| `ConnectionError` | Keycloak недоступен | Проверьте сеть, URL |
| `ValidationError` | Ошибка в config.yaml | Проверьте синтаксис YAML |

### 7.2. Логи

**Файл логов:** `keycloak_generator.log`

**Просмотр:**
```bash
# Последние строки
tail keycloak_generator.log

# Все логи
cat keycloak_generator.log

# Поиск ошибок
grep ERROR keycloak_generator.log
```

**Уровни логов:**
- `INFO` — нормальные операции
- `WARNING` — предупреждения
- `ERROR` — ошибки
- `DEBUG` — детальная отладка

### 7.3. Повторный запуск

**Если часть пользователей создана:**

```bash
# Просто запустите снова
python -m keycloak_userator.cli --no-interactive
```

**Программа:**
- Проверит существующих пользователей
- Пропустит созданных
- Создаст недостающих

**Идемпотентность гарантирована!**

---

## 8. Безопасность

### 8.1. Хранение учётных данных

**✅ Делайте:**
- Храните файлы в защищённой папке
- Используйте шифрование диска
- Удаляйте файлы после передачи
- Ограничивайте доступ (chmod 600)

**❌ Не делайте:**
- Не храните файлы в облаке без шифрования
- Не отправляйте пароли в открытом виде
- Не коммитьте `.env` в git
- Не оставляйте файлы на общем компьютере

### 8.2. Защита .env файла

```bash
# Ограничение доступа (Linux)
chmod 600 .env

# Проверка
ls -l .env
# -rw------- 1 user user ... .env
```

### 8.3. Удаление файлов

```bash
# После передачи учётных данных
rm -rf output/credentials_*.txt
rm -rf output/credentials_*.csv
rm -rf output/credentials_*.json

# Очистка логов (опционально)
rm keycloak_generator.log
```

---

## 9. Часто задаваемые вопросы

### 9.1. Как создать пользователей для другого курса?

**Вариант 1:** Изменить config.yaml
```yaml
user:
  login_prefix: "math2025"
  email_domain: "university.edu"
  group_name: "math-users"
```

**Вариант 2:** Использовать другой файл
```bash
python -m keycloak_userator.cli --config configs/math_course.yaml
```

### 9.2. Как добавить существующих пользователей в группу?

**Через Keycloak UI:**
1. Откройте Keycloak Admin Console
2. Перейдите в Users → View all users
3. Выберите пользователей (checkbox)
4. Нажмите «Add to group»
5. Выберите группу

**Через скрипт:**
```bash
# Требуется доработка функционала
# См. руководство программиста
```

### 9.3. Как изменить пароль пользователю?

**Через Keycloak UI:**
1. Откройте Keycloak Admin Console
2. Users → Найдите пользователя
3. Credentials → Reset Password
4. Введите новый пароль
5. Save

**Массовое изменение:**
- Требуется доработка скрипта
- См. руководство программиста

### 9.4. Как удалить созданных пользователей?

**Через Keycloak UI:**
1. Users → View all users
2. Найдите по префиксу (например, `enginc_`)
3. Выделите всех
4. Delete

**Через скрипт (требуется доработка):**
```python
# См. руководство программиста
# Функция delete_users(prefix)
```

---

## 10. Поддержка

### 10.1. Логи для отладки

При обращении за помощью приложите:

1. **Версию программы:**
   ```bash
   python -c "import keycloak_userator; print(keycloak_userator.__version__)"
   ```

2. **Фрагмент логов:**
   ```bash
   tail -100 keycloak_generator.log
   ```

3. **Конфигурацию (без паролей!):**
   ```bash
   cat config.yaml
   cat .env.example  # НЕ .env!
   ```

### 10.2. Контакты

- Документация: `docs/`
- Issues: GitHub repository
- Email: разработчику

---

*Документ создан: 2026-03-28*
*Версия документа: 1.0*
