# Руководство программиста

## 1. Введение

Это руководство предназначено для разработчиков, которые будут:
- Расширять функциональность программы
- Интегрировать программу в другие проекты
- Поддерживать и модифицировать код

**Требуемые знания:**
- Python 3.12+ (уверенное владение)
- Type hints и dataclasses
- Работа с API (HTTP, REST)
- Тестирование (pytest)

---

## 2. Структура проекта

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
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_password.py
│   ├── test_exporter.py
│   └── test_keycloak_client.py
├── docs/                    # Документация
└── README.md               # Основная документация
```

---

## 3. Установка для разработки

### 3.1. Клонирование

```bash
git clone <repository-url>
cd kk-userator
```

### 3.2. Виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 3.3. Установка зависимостей

```bash
# Установка как пакета
pip install -e .

# Для разработки (опционально)
pip install -e ".[dev]"
```

### 3.4. Настройка окружения

```bash
# Копирование примера
cp .env.example .env

# Редактирование .env
nano .env  # или ваш редактор
```

---

## 4. Архитектурные принципы

### 4.1. Разделение ответственности

Каждый модуль отвечает за одну область:

| Модуль | Ответственность |
|--------|-----------------|
| `cli.py` | Парсинг аргументов, оркестрация |
| `config.py` | Загрузка, валидация конфигурации |
| `types.py` | Структуры данных |
| `password.py` | Генерация паролей |
| `exporter.py` | Экспорт в файлы |
| `keycloak_client.py` | Keycloak API |

### 4.2. Внедрение зависимостей

Зависимости внедряются через конструктор:

```python
class KeycloakUserGenerator:
    def __init__(
        self,
        keycloak_admin: KeycloakAdmin,
        password_generator: PasswordGenerator,
        exporter: CredentialExporter,
        config: Config,
        dry_run: bool = False
    ):
        self.keycloak_admin = keycloak_admin
        self.password_generator = password_generator
        self.exporter = exporter
        self.config = config
        self.dry_run = dry_run
```

**Преимущества:**
- Лёгкое тестирование с моками
- Явные зависимости
- Гибкость замены реализаций

### 4.3. Обработка ошибок

```python
try:
    user_id = self.keycloak_admin.create_user(new_user)
except KeycloakError as e:
    self.logger.error(f"Ошибка создания пользователя: {e}")
    self.stats['errors'] += 1
    return False
except Exception as e:
    self.logger.exception(f"Неожиданная ошибка: {e}")
    return False
```

**Принципы:**
- Ловить конкретные исключения
- Логировать с контекстом
- Возвращать статус успеха/ошибки
- Не прерывать пакет из-за одной ошибки

---

## 5. Расширение функциональности

### 5.1. Добавление нового формата экспорта

**Шаг 1:** Создать стратегию экспорта

```python
# exporter.py
class XMLExportStrategy(ExportStrategy):
    """Экспорт в XML формате."""
    
    def export(
        self,
        users: List[UserCredentials],
        path: Path
    ) -> str:
        root = ET.Element("users")
        
        for user in users:
            user_elem = ET.SubElement(root, "user")
            ET.SubElement(user_elem, "username").text = user.username
            ET.SubElement(user_elem, "password").text = user.password
            # ...
        
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
        
        return str(path)
```

**Шаг 2:** Добавить стратегию в экспортёр

```python
class CredentialExporter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.strategies = {
            'csv': CSVExportStrategy(),
            'txt': TXTExportStrategy(),
            'json': JSONExportStrategy(),
            'xml': XMLExportStrategy(),  # ← Добавить
        }
```

**Шаг 3:** Добавить тесты

```python
# tests/test_exporter.py
def test_export_xml(tmp_path):
    exporter = CredentialExporter(str(tmp_path))
    users = [create_test_user()]
    
    result = exporter.export(users, formats=['xml'])
    
    assert 'xml' in result
    assert Path(result['xml']).exists()
```

### 5.2. Добавление новой валидации

**Шаг 1:** Создать функцию валидации

```python
# config.py
def validate_login_prefix(prefix: str) -> None:
    """Проверка префикса для логинов."""
    if not prefix:
        raise ConfigValidationError("Префикс не может быть пустым")
    
    if len(prefix) > 32:
        raise ConfigValidationError(
            f"Префикс слишком длинный: {len(prefix)} > 32"
        )
    
    # Проверка на кириллицу
    if any('\u0400' <= c <= '\u04FF' for c in prefix):
        raise ConfigValidationError(
            "Префикс должен содержать только латиницу"
        )
```

**Шаг 2:** Вызвать в загрузчике конфигурации

```python
class ConfigLoader:
    def _validate_user_config(self, user_data: dict) -> None:
        validate_login_prefix(user_data.get('login_prefix', ''))
        validate_email_domain(user_data.get('email_domain', ''))
        # ...
```

**Шаг 3:** Добавить тесты

```python
# tests/test_config.py
def test_validate_login_prefix_cyrillic():
    with pytest.raises(ConfigValidationError):
        validate_login_prefix("студент")
```

### 5.3. Добавление нового параметра командной строки

**Шаг 1:** Добавить в парсер

```python
# cli.py
def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    
    parser.add_argument(
        '--prefix', '-p',
        type=str,
        default=None,
        help='Префикс для логинов (переопределяет config.yaml)'
    )
    
    return parser
```

**Шаг 2:** Обработать в загрузке конфигурации

```python
def load_application_config(args: argparse.Namespace) -> Config:
    config = load_config(args.config)
    
    if args.prefix is not None:
        config.user.login_prefix = args.prefix
    
    return config
```

**Шаг 3:** Добавить тесты

```python
# tests/test_cli.py
def test_parse_prefix_argument():
    parser = create_argument_parser()
    args = parser.parse_args(['--prefix', 'test'])
    
    assert args.prefix == 'test'
```

---

## 6. Тестирование

### 6.1. Запуск тестов

```bash
# Все тесты
pytest

# С выводом покрытия
pytest --cov=keycloak_userator --cov-report=term-missing

# С выводом ошибок
pytest -v

# Конкретный тест
pytest tests/test_password.py::TestPasswordGenerator::test_generate_length -v
```

### 6.2. Написание тестов

**Структура теста:**

```python
# tests/test_password.py
import pytest
from keycloak_userator.password import PasswordGenerator

class TestPasswordGenerator:
    """Тесты генератора паролей."""
    
    def test_generate_returns_string(self):
        """Генерация возвращает строку."""
        gen = PasswordGenerator(length=8)
        password = gen.generate()
        
        assert isinstance(password, str)
    
    def test_generate_has_correct_length(self):
        """Длина пароля соответствует настройке."""
        gen = PasswordGenerator(length=12)
        password = gen.generate()
        
        assert len(password) == 12
    
    def test_generate_unique_passwords(self):
        """Пароли уникальны."""
        gen = PasswordGenerator()
        passwords = [gen.generate() for _ in range(100)]
        
        assert len(set(passwords)) == 100
```

**Фикстуры:**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def test_user():
    """Создание тестового пользователя."""
    return UserCredentials(
        username='test_user',
        password='test_password',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        enabled=True
    )

@pytest.fixture
def mock_keycloak_admin(mocker):
    """Мок KeycloakAdmin."""
    mock = mocker.Mock()
    mock.create_user.return_value = 'test-user-id'
    mock.get_users.return_value = []
    return mock
```

### 6.3. Мокирование внешних зависимостей

```python
# tests/test_keycloak_client.py
def test_create_user_calls_api(mocker):
    """Создание пользователя вызывает API."""
    mock_admin = mocker.Mock()
    mock_admin.create_user.return_value = 'user-id'
    
    client = KeycloakUserGenerator(
        keycloak_admin=mock_admin,
        config=test_config
    )
    
    result = client._create_user(
        username='test',
        password='pass',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    
    assert result is True
    mock_admin.create_user.assert_called_once()
```

---

## 7. Статический анализ

### 7.1. Линтинг (Ruff)

```bash
# Проверка
ruff check keycloak_userator/

# Автоисправление
ruff check keycloak_userator/ --fix
```

### 7.2. Проверка типов (Mypy)

```bash
# Проверка
mypy keycloak_userator/

# Строгий режим
mypy keycloak_userator/ --strict
```

### 7.3. Безопасность (Bandit)

```bash
# Проверка безопасности
bandit -r keycloak_userator/
```

---

## 8. Отладка

### 8.1. Логирование

```python
import logging

logger = logging.getLogger('keycloak_user_generator')

# Уровни логирования
logger.debug("Детальная информация")    # Отладка
logger.info("Операция выполнена")       # Информация
logger.warning("Предупреждение")        # Предупреждение
logger.error("Ошибка")                  # Ошибка
logger.critical("Критическая ошибка")   # Критическая
```

### 8.2. Отладочная сессия

```bash
# Запуск с подробным логом
python -m keycloak_userator.cli --dry-run --count 5

# Лог файл
tail -f keycloak_generator.log
```

### 8.3. Отладчик (pdb)

```python
# В коде
def generate_users(self, count: int):
    import pdb; pdb.set_trace()  # ← Точка останова
    # ...
```

```bash
# Запуск
python -m keycloak_userator.cli
```

---

## 9. Сборка и распространение

### 9.1. Создание пакета

```bash
# Установка инструментов
pip install build twine

# Сборка
python -m build

# Проверка
twine check dist/*
```

### 9.2. Публикация в PyPI (опционально)

```bash
# Тестовый PyPI
twine upload --repository testpypi dist/*

# Продакшен PyPI
twine upload dist/*
```

### 9.3. Установка из пакета

```bash
# Из PyPI
pip install kk-userator

# Из файла
pip install dist/kk_userator-2.0.0-py3-none-any.whl
```

---

## 10. Вклад в проект

### 10.1. Ветвление

```bash
# Создание ветки
git checkout -b feature/new-export-format

# Именование веток
feature/<описание>     # Новая функциональность
fix/<описание>         # Исправление бага
refactor/<описание>    # Рефакторинг
docs/<описание>        # Документация
```

### 10.2. Коммиты

```bash
# Формат: type(scope): description
git commit -m "feat(exporter): добавить XML экспорт"
git commit -m "fix(password): исправить генерацию спецсимволов"
git commit -m "docs(readme): обновить примеры использования"
```

### 10.3. Pull Request

1. Создать ветку
2. Внести изменения
3. Запустить тесты
4. Создать PR
5. Пройти code review
6. Влить в main

---

*Документ создан: 2026-03-28*
*Версия документа: 1.0*
