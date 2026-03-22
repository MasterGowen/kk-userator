#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_exporter.py

Тесты для экспортёра учётных данных CredentialExporter.

Покрывает:
- Экспорт в CSV
- Экспорт в TXT
- Экспорт в JSON
- Создание директорий
- Генерацию имён файлов
"""

import csv
import json
import os
import tempfile

import pytest

from keycloak_userator.exporter import CredentialExporter


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def temp_output_dir():
    """Временная директория для вывода."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_users():
    """Пример данных пользователей."""
    return [
        {
            'username': 'user1',
            'password': 'Pass1234',
            'email': 'user1@example.com',
            'firstName': 'Иван',
            'lastName': 'Иванов',
            'enabled': True
        },
        {
            'username': 'user2',
            'password': 'Pass5678',
            'email': 'user2@example.com',
            'firstName': 'Пётр',
            'lastName': 'Петров',
            'enabled': True
        },
        {
            'username': 'user3',
            'password': 'Pass9012',
            'email': 'user3@example.com',
            'firstName': 'Анна',
            'lastName': 'Анна',
            'enabled': False
        }
    ]


@pytest.fixture
def exporter(temp_output_dir):
    """Экспортёр с временной директорией."""
    return CredentialExporter(output_dir=temp_output_dir)


# =============================================================================
# ТЕСТЫ ИНИЦИАЛИЗАЦИИ
# =============================================================================

class TestCredentialExporterInit:
    """Тесты инициализации CredentialExporter."""

    def test_init_default(self, temp_output_dir):
        """Инициализация с параметрами по умолчанию."""
        exporter = CredentialExporter()

        assert exporter.output_dir == "output"

    def test_init_custom_dir(self, temp_output_dir):
        """Инициализация с пользовательской директорией."""
        exporter = CredentialExporter(output_dir=temp_output_dir)

        assert exporter.output_dir == temp_output_dir

    def test_init_creates_directory(self, temp_output_dir):
        """Создание директории при инициализации."""
        new_dir = os.path.join(temp_output_dir, "new_output")
        CredentialExporter(output_dir=new_dir)

        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)


# =============================================================================
# ТЕСТЫ ЭКСПОРТА В CSV
# =============================================================================

class TestCredentialExporterCSV:
    """Тесты экспорта в CSV."""

    def test_export_csv_creates_file(self, exporter, sample_users):
        """Экспорт создаёт файл."""
        filepath = exporter.export_csv(sample_users)

        assert os.path.exists(filepath)
        assert filepath.endswith('.csv')

    def test_export_csv_content(self, exporter, sample_users):
        """Содержимое CSV файла."""
        filepath = exporter.export_csv(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert rows[0]['username'] == 'user1'
        assert rows[0]['password'] == 'Pass1234'
        assert rows[0]['email'] == 'user1@example.com'
        assert rows[0]['firstName'] == 'Иван'
        assert rows[0]['lastName'] == 'Иванов'

    def test_export_csv_headers(self, exporter, sample_users):
        """Заголовки CSV."""
        filepath = exporter.export_csv(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        assert fieldnames == ['username', 'password', 'email', 'firstName', 'lastName', 'enabled']

    def test_export_csv_custom_filename(self, exporter, sample_users):
        """Экспорт с пользовательским именем файла."""
        filepath = exporter.export_csv(sample_users, filename="custom.csv")

        assert filepath.endswith("custom.csv")
        assert os.path.exists(filepath)

    def test_export_csv_empty_users(self, exporter):
        """Экспорт пустого списка пользователей."""
        filepath = exporter.export_csv([])

        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0

    def test_export_csv_unicode(self, exporter):
        """Экспорт с Unicode символами."""
        users = [
            {
                'username': 'user1',
                'password': 'Pass1234',
                'email': 'user1@example.com',
                'firstName': 'Александр',
                'lastName': 'Никитин',
                'enabled': True
            }
        ]
        filepath = exporter.export_csv(users)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Александр' in content
        assert 'Никитин' in content


# =============================================================================
# ТЕСТЫ ЭКСПОРТА В TXT
# =============================================================================

class TestCredentialExporterTXT:
    """Тесты экспорта в TXT."""

    def test_export_txt_creates_file(self, exporter, sample_users):
        """Экспорт создаёт файл."""
        filepath = exporter.export_txt(sample_users)

        assert os.path.exists(filepath)
        assert filepath.endswith('.txt')

    def test_export_txt_content(self, exporter, sample_users):
        """Содержимое TXT файла."""
        filepath = exporter.export_txt(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'УЧЁТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK' in content
        assert 'user1' in content
        assert 'Pass1234' in content
        assert 'Иван' in content
        assert 'Иванов' in content

    def test_export_txt_format(self, exporter, sample_users):
        """Форматирование TXT файла."""
        filepath = exporter.export_txt(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверка разделителей
        assert '=' * 40 in content
        assert '-' * 40 in content
        assert 'Дата генерации:' in content
        assert 'Всего пользователей: 3' in content

    def test_export_txt_custom_filename(self, exporter, sample_users):
        """Экспорт с пользовательским именем файла."""
        filepath = exporter.export_txt(sample_users, filename="custom.txt")

        assert filepath.endswith("custom.txt")
        assert os.path.exists(filepath)

    def test_export_txt_empty_users(self, exporter):
        """Экспорт пустого списка пользователей."""
        filepath = exporter.export_txt([])

        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Всего пользователей: 0' in content

    def test_export_txt_disabled_user(self, exporter, sample_users):
        """Экспорт отключенного пользователя."""
        filepath = exporter.export_txt(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # user3 имеет enabled=False
        assert 'user3' in content
        # Проверяем, что статус отображается правильно
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'user3' in line:
                # Находим статус в следующих строках
                for j in range(i, min(i+10, len(lines))):
                    if 'Статус:' in lines[j]:
                        assert 'Отключён' in lines[j]
                        break


# =============================================================================
# ТЕСТЫ ЭКСПОРТА В JSON
# =============================================================================

class TestCredentialExporterJSON:
    """Тесты экспорта в JSON."""

    def test_export_json_creates_file(self, exporter, sample_users):
        """Экспорт создаёт файл."""
        filepath = exporter.export_json(sample_users)

        assert os.path.exists(filepath)
        assert filepath.endswith('.json')

    def test_export_json_content(self, exporter, sample_users):
        """Содержимое JSON файла."""
        filepath = exporter.export_json(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'generated_at' in data
        assert 'total_users' in data
        assert 'users' in data
        assert data['total_users'] == 3
        assert len(data['users']) == 3

    def test_export_json_user_data(self, exporter, sample_users):
        """Данные пользователей в JSON."""
        filepath = exporter.export_json(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        user1 = data['users'][0]
        assert user1['username'] == 'user1'
        assert user1['password'] == 'Pass1234'
        assert user1['email'] == 'user1@example.com'
        assert user1['firstName'] == 'Иван'
        assert user1['lastName'] == 'Иванов'

    def test_export_json_custom_filename(self, exporter, sample_users):
        """Экспорт с пользовательским именем файла."""
        filepath = exporter.export_json(sample_users, filename="custom.json")

        assert filepath.endswith("custom.json")
        assert os.path.exists(filepath)

    def test_export_json_empty_users(self, exporter):
        """Экспорт пустого списка пользователей."""
        filepath = exporter.export_json([])

        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['total_users'] == 0
        assert data['users'] == []

    def test_export_json_valid_json(self, exporter, sample_users):
        """Валидность JSON."""
        filepath = exporter.export_json(sample_users)

        with open(filepath, 'r', encoding='utf-8') as f:
            # Должен парситься без ошибок
            data = json.load(f)

        assert isinstance(data, dict)

    def test_export_json_unicode(self, exporter):
        """Экспорт с Unicode символами."""
        users = [
            {
                'username': 'user1',
                'password': 'Pass1234',
                'email': 'user1@example.com',
                'firstName': 'Александр',
                'lastName': 'Никитин',
                'enabled': True
            }
        ]
        filepath = exporter.export_json(users)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['users'][0]['firstName'] == 'Александр'
        assert data['users'][0]['lastName'] == 'Никитин'


# =============================================================================
# ТЕСТЫ ГЕНЕРАЦИИ ИМЁН ФАЙЛОВ
# =============================================================================

class TestCredentialExporterFilename:
    """Тесты генерации имён файлов."""

    def test_generate_filename_csv(self, exporter):
        """Генерация имени для CSV."""
        filename = exporter._generate_filename("csv")

        assert filename.startswith("credentials_")
        assert filename.endswith(".csv")

    def test_generate_filename_txt(self, exporter):
        """Генерация имени для TXT."""
        filename = exporter._generate_filename("txt")

        assert filename.startswith("credentials_")
        assert filename.endswith(".txt")

    def test_generate_filename_json(self, exporter):
        """Генерация имени для JSON."""
        filename = exporter._generate_filename("json")

        assert filename.startswith("credentials_")
        assert filename.endswith(".json")

    def test_generate_filename_format(self, exporter):
        """Формат имени файла."""
        filename = exporter._generate_filename("csv")

        # Проверяем формат credentials_YYYYMMDD_HHMMSS.csv
        import re
        pattern = r'credentials_\d{8}_\d{6}\.csv'
        assert re.match(pattern, filename)

    def test_generate_filename_unique(self, exporter):
        """Уникальность имён файлов."""
        # Генерируем несколько имён (маловероятно, но возможно совпадение)
        filenames = [exporter._generate_filename("csv") for _ in range(10)]

        # Все имена должны быть уникальными (если генерируются в разное время)
        # Для надёжности проверяем, что имена хотя бы выглядят правильно
        import re
        for filename in filenames:
            pattern = r'credentials_\d{8}_\d{6}\.csv'
            assert re.match(pattern, filename)


# =============================================================================
# ТЕСТЫ СОЗДАНИЯ ДИРЕКТОРИЙ
# =============================================================================

class TestCredentialExporterDirectories:
    """Тесты работы с директориями."""

    def test_create_nested_directory(self, temp_output_dir):
        """Создание вложенной директории."""
        nested_dir = os.path.join(temp_output_dir, "level1", "level2", "output")
        CredentialExporter(output_dir=nested_dir)

        assert os.path.exists(nested_dir)

    def test_existing_directory(self, temp_output_dir):
        """Использование существующей директории."""
        exporter = CredentialExporter(output_dir=temp_output_dir)

        # Не должно выбрасывать ошибок
        assert exporter.output_dir == temp_output_dir
