# 🛠️ Python Code Review Toolchain — Инструменты для ревьюера

**Назначение:** Набор инструментов с детерминированными алгоритмами для объективного ревью Python-кода.

---

## 📋 Проблема

**Ревьюер (LLM) без инструментов:**
- Субъективная оценка («код читаем» / «код не читаем»)
- Пропуск багов (не видит все места использования переменной)
- Непредсказуемость (разные выводы при одинаковом коде)
- Медленная проверка (токен за токеном)

**Ревьюер с инструментами:**
- ✅ Объективные метрики (цикломатическая сложность, покрытие)
- ✅ Детерминированные результаты (одинаковый код = одинаковый отчёт)
- ✅ Полнота проверки (все файлы, все строки)
- ✅ Скорость (секунды вместо минут)

---

## 🎯 Рекомендуемый набор инструментов

### 1. Ruff — линтер (заменяет Flake8 + PyLint)

**Назначение:** Проверка стиля, багов, anti-patterns.

**Почему Ruff:**
| Метрика | Ruff | Flake8 + PyLint |
|---------|------|-----------------|
| Скорость (120K строк) | 0.2 сек | 14-23 сек |
| Скорость (CI, 2 vCPU) | 19 сек | 100 сек |
| Проверки | 500+ (Flake8 + PyLint + Bugbear) | Зависит от плагинов |

**Установка:**
```bash
pip install ruff
```

**Запуск:**
```bash
ruff check src/
ruff format src/  # Авто-форматирование
```

**Конфигурация (`pyproject.toml`):**
```toml
[tool.ruff]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "RUF",    # Ruff-specific rules
]
line-length = 100
```

**Что находит:**
- ❌ Синтаксические ошибки
- ❌ Неиспользуемые импорты
- ❌ Нарушения PEP 8
- ❌ Опасные паттерны (например, захват переменной цикла в замыкании)
- ❌ Устаревший синтаксис

---

### 2. MyPy — статическая проверка типов

**Назначение:** Поиск ошибок типизации до запуска кода.

**Почему MyPy:**
- ✅ Находит ошибки времени выполнения на этапе разработки
- ✅ Постепенная типизация (можно добавлять аннотации частично)
- ✅ Интеграция с CI/CD

**Установка:**
```bash
pip install mypy
```

**Запуск:**
```bash
mypy src/
mypy --strict src/  # Строгий режим
```

**Что находит:**
- ❌ Несоответствие типов аргументов
- ❌ Несоответствие типов возврата
- ❌ Отсутствие аннотаций (в строгом режиме)
- ❌ Ошибки с Optional/Union типами

**Пример:**
```python
def add(a: int, b: int) -> int:
    return a + b

add(1, "2")  # MyPy: error: Argument 2 has incompatible type "str"
```

---

### 3. Bandit — проверка безопасности

**Назначение:** Поиск уязвимостей безопасности в Python-коде.

**Почему Bandit:**
- ✅ Специализирован для Python
- ✅ 60+ проверок безопасности
- ✅ Отчётность по уровню риска (Low/Medium/High)

**Установка:**
```bash
pip install bandit
```

**Запуск:**
```bash
bandit -r src/
bandit -r src/ -ll  # Только Medium и High
```

**Что находит:**
- ❌ Использование `eval()` / `exec()`
- ❌ Hardcoded пароли/ключи
- ❌ Слабые криптографические функции (MD5, SHA1)
- ❌ SQL-инъекции
- ❌ Использование `pickle` с ненадёжными данными
- ❌ Проблемы с SSL/TLS

---

### 4. Coverage.py — покрытие тестами

**Назначение:** Измерение процента кода, покрытого тестами.

**Почему Coverage.py:**
- ✅ Стандарт де-факто для Python
- ✅ Отчётность по строкам/веткам
- ✅ Интеграция с CI/CD

**Установка:**
```bash
pip install coverage pytest-cov
```

**Запуск:**
```bash
coverage run -m pytest
coverage report
coverage html  # HTML-отчёт
```

**Порог качества:**
- ✅ > 80% — хорошо
- ⚠️ 60-80% — приемлемо
- ❌ < 60% — требует улучшения

---

### 5. Radon / Xenon — метрики сложности

**Назначение:** Измерение цикломатической сложности, поддержание читаемости.

**Почему Radon:**
- ✅ Цикломатическая сложность (Cyclomatic Complexity)
- ✅ Halstead-метрики
- ✅ Поддержание читаемости кода

**Установка:**
```bash
pip install radon xenon
```

**Запуск:**
```bash
radon cc src/  # Cyclomatic complexity
radon mi src/  # Maintainability Index
xenon --max-absolute B src/  # Порог сложности
```

**Пороги:**
| Метрика | Порог | Значение |
|---------|-------|----------|
| Cyclomatic Complexity | < 10 (A), < 20 (B) | Количество путей выполнения |
| Maintainability Index | > 65 | Чем выше, тем лучше |

---

## 📊 Чек-лист ревьюера с инструментами

**Перед ревью (автоматическая проверка):**
```bash
# 1. Линтер
ruff check src/ && echo "✅ Ruff: OK" || echo "❌ Ruff: FAIL"

# 2. Типы
mypy src/ && echo "✅ MyPy: OK" || echo "❌ MyPy: FAIL"

# 3. Безопасность
bandit -r src/ -ll && echo "✅ Bandit: OK" || echo "❌ Bandit: FAIL"

# 4. Тесты
coverage run -m pytest && coverage report --fail-under=80

# 5. Сложность
xenon --max-absolute B src/ && echo "✅ Xenon: OK" || echo "❌ Xenon: FAIL"
```

**Результат для ревьюера:**
```
┌─────────────────────────────────────────────────────┐
│              Code Quality Report                    │
├─────────────────────────────────────────────────────┤
│ Ruff:          ✅ 0 ошибок, 2 предупреждения        │
│ MyPy:          ✅ Все типы корректны                │
│ Bandit:        ⚠️ 1 Medium (hardcoded key)          │
│ Coverage:      ✅ 87% (порог: 80%)                  │
│ Xenon:         ✅ Средняя сложность: 8 (B)          │
└─────────────────────────────────────────────────────┘
```

**Ручное ревью (после автоматической проверки):**
- ✅ Инструменты прошли → проверяю логику, архитектуру
- ❌ Инструменты не прошли → возвращаю автору на исправление

---

## 🔗 Интеграция в CI/CD

**GitHub Actions (`.github/workflows/ci.yml`):**
```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy bandit coverage xenon
          pip install -r requirements.txt
      
      - name: Ruff lint
        run: ruff check src/
      
      - name: MyPy types
        run: mypy src/
      
      - name: Bandit security
        run: bandit -r src/ -ll
      
      - name: Coverage
        run: |
          coverage run -m pytest
          coverage report --fail-under=80
      
      - name: Xenon complexity
        run: xenon --max-absolute B src/
```

---

## 📈 Метрики качества

| Метрика | Инструмент | Порог | Критичность |
|---------|------------|-------|-------------|
| Линтинг (ошибки) | Ruff | 0 | 🔴 Критично |
| Линтинг (предупреждения) | Ruff | < 10 | 🟡 Важно |
| Типы | MyPy | 100% pass | 🔴 Критично |
| Безопасность | Bandit | 0 High, < 3 Medium | 🔴 Критично |
| Покрытие тестами | Coverage | > 80% | 🟡 Важно |
| Цикломатическая сложность | Xenon | < B (20) | 🟡 Важно |

---

## 🎯 Рекомендации для Reviewer (агент)

**Промпт для ревьюера с инструментами:**

```
Ты — ревьюер кода с инструментами статического анализа.

Твоя работа:
1. Запусти инструменты (Ruff, MyPy, Bandit, Coverage, Xenon)
2. Получи отчёты
3. Классифицируй проблемы:
   - 🔴 Критично: инструменты не прошли (ошибки, уязвимости)
   - 🟡 Важно: предупреждения, метрики на границе
   - 🟢 Рекомендация: улучшения без блокировки
4. Верни структурированный отчёт

Формат отчёта:
```
## Автоматическая проверка

| Инструмент | Статус | Детали |
|------------|--------|--------|
| Ruff | ✅ | 0 ошибок, 2 предупреждения |
| MyPy | ✅ | Все типы корректны |
| Bandit | ⚠️ | 1 Medium: hardcoded key (строка 45) |
| Coverage | ✅ | 87% |
| Xenon | ✅ | Сложность B |

## Ручное ревью

### Логика
- [ ] ...

### Архитектура
- [ ] ...

### Безопасность (кроме Bandit)
- [ ] ...

## Вердикт

Статус: Request Changes / Comment / Approve
```
```

---

## 🔗 Источники

- [Best Python Static Code Analysis Tools in 2026](https://www.code-quality.io/best-python-static-code-analysis-tools)
- [Goodbye to Flake8 and PyLint: faster linting with Ruff](https://pythonspeed.com/articles/pylint-flake8-ruff/)
- [Bandit: Security Issues in Python Code](https://github.com/PyCQA/bandit)
- [MyPy: Static Type Checker](https://mypy-lang.org/)

---

*Версия: 1.0*
*Дата: 2026-03-19*
*Статус: Готово к использованию*
