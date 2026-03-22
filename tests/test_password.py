#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_password.py

Тесты для генератора паролей PasswordGenerator.

Покрывает:
- Генерацию одного пароля
- Генерацию батча паролей
- Валидацию длины
- Наборы символов
"""

import string

import pytest

from keycloak_userator.config import Config, PasswordConfig, UserConfig, DefaultsConfig, LoggingConfig
from keycloak_userator.password import PasswordGenerator


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def default_config():
    """Конфигурация по умолчанию."""
    return Config(
        user=UserConfig(),
        password=PasswordConfig(),
        defaults=DefaultsConfig(),
        logging=LoggingConfig()
    )


@pytest.fixture
def custom_password_config():
    """Пользовательская конфигурация паролей."""
    return Config(
        user=UserConfig(),
        password=PasswordConfig(
            length=16,
            use_lowercase=True,
            use_uppercase=True,
            use_digits=True,
            use_special=False
        ),
        defaults=DefaultsConfig(),
        logging=LoggingConfig()
    )


@pytest.fixture
def simple_password_config():
    """Простая конфигурация (только строчные буквы)."""
    return Config(
        user=UserConfig(),
        password=PasswordConfig(
            length=8,
            use_lowercase=True,
            use_uppercase=False,
            use_digits=False,
            use_special=False
        ),
        defaults=DefaultsConfig(),
        logging=LoggingConfig()
    )


# =============================================================================
# ТЕСТЫ ИНИЦИАЛИЗАЦИИ
# =============================================================================

class TestPasswordGeneratorInit:
    """Тесты инициализации PasswordGenerator."""

    def test_init_default(self, default_config):
        """Инициализация с конфигурацией по умолчанию."""
        gen = PasswordGenerator(default_config)

        assert gen.length == 8
        assert len(gen.chars) > 0

    def test_init_custom_length(self, custom_password_config):
        """Инициализация с пользовательской длиной."""
        gen = PasswordGenerator(custom_password_config)

        assert gen.length == 16

    def test_init_charsets(self, default_config):
        """Инициализация с наборами символов."""
        gen = PasswordGenerator(default_config)

        # По умолчанию должны быть lowercase, uppercase, digits
        assert all(c in gen.chars for c in 'abc')
        assert all(c in gen.chars for c in 'ABC')
        assert all(c in gen.chars for c in '012')


# =============================================================================
# ТЕСТЫ ГЕНЕРАЦИИ ПАРОЛЕЙ
# =============================================================================

class TestPasswordGeneratorGenerate:
    """Тесты генерации паролей."""

    def test_generate_single(self, default_config):
        """Генерация одного пароля."""
        gen = PasswordGenerator(default_config)
        password = gen.generate()

        assert isinstance(password, str)
        assert len(password) == 8

    def test_generate_length(self, custom_password_config):
        """Длина сгенерированного пароля."""
        gen = PasswordGenerator(custom_password_config)
        password = gen.generate()

        assert len(password) == 16

    def test_generate_different_passwords(self, default_config):
        """Генерация разных паролей."""
        gen = PasswordGenerator(default_config)
        passwords = [gen.generate() for _ in range(10)]

        # Все пароли должны быть уникальными (крайне низкая вероятность коллизии)
        assert len(set(passwords)) == 10

    def test_generate_contains_valid_chars(self, default_config):
        """Пароль содержит только допустимые символы."""
        gen = PasswordGenerator(default_config)
        password = gen.generate()

        for char in password:
            assert char in gen.chars

    def test_generate_simple_charset(self, simple_password_config):
        """Генерация с простым набором символов."""
        gen = PasswordGenerator(simple_password_config)
        password = gen.generate()

        assert len(password) == 8
        assert all(c in string.ascii_lowercase for c in password)

    def test_generate_has_lowercase(self, default_config):
        """Пароль содержит строчные буквы."""
        gen = PasswordGenerator(default_config)
        password = gen.generate()

        assert any(c in string.ascii_lowercase for c in password)

    def test_generate_has_uppercase(self, default_config):
        """Пароль содержит заглавные буквы."""
        gen = PasswordGenerator(default_config)
        password = gen.generate()

        assert any(c in string.ascii_uppercase for c in password)

    def test_generate_has_digits(self, default_config):
        """Пароль содержит цифры."""
        gen = PasswordGenerator(default_config)
        # Генерируем несколько паролей для надёжности
        passwords = gen.generate_batch(10)

        # Хотя бы один пароль должен содержать цифры
        has_digits = any(
            any(c in string.digits for c in pwd)
            for pwd in passwords
        )
        assert has_digits is True


# =============================================================================
# ТЕСТЫ ПАКЕТНОЙ ГЕНЕРАЦИИ
# =============================================================================

class TestPasswordGeneratorBatch:
    """Тесты пакетной генерации паролей."""

    def test_generate_batch(self, default_config):
        """Генерация батча паролей."""
        gen = PasswordGenerator(default_config)
        passwords = gen.generate_batch(10)

        assert isinstance(passwords, list)
        assert len(passwords) == 10

    def test_generate_batch_length(self, custom_password_config):
        """Длина паролей в батче."""
        gen = PasswordGenerator(custom_password_config)
        passwords = gen.generate_batch(5)

        for password in passwords:
            assert len(password) == 16

    def test_generate_batch_unique(self, default_config):
        """Уникальность паролей в батче."""
        gen = PasswordGenerator(default_config)
        passwords = gen.generate_batch(100)

        # Все пароли должны быть уникальными
        assert len(set(passwords)) == 100

    def test_generate_batch_empty(self, default_config):
        """Генерация пустого батча."""
        gen = PasswordGenerator(default_config)
        passwords = gen.generate_batch(0)

        assert passwords == []
        assert isinstance(passwords, list)

    def test_generate_batch_large(self, default_config):
        """Генерация большого батча."""
        gen = PasswordGenerator(default_config)
        passwords = gen.generate_batch(1000)

        assert len(passwords) == 1000
        # Проверяем уникальность (для 1000 паролей вероятность коллизии крайне мала)
        assert len(set(passwords)) == 1000


# =============================================================================
# ТЕСТЫ ВАЛИДАЦИИ ДЛИНЫ
# =============================================================================

class TestPasswordGeneratorValidation:
    """Тесты валидации параметров."""

    def test_min_length(self):
        """Минимальная длина пароля."""
        config = Config(
            user=UserConfig(),
            password=PasswordConfig(length=6),
            defaults=DefaultsConfig(),
            logging=LoggingConfig()
        )
        gen = PasswordGenerator(config)
        password = gen.generate()

        assert len(password) == 6

    def test_max_length(self):
        """Максимальная длина пароля."""
        config = Config(
            user=UserConfig(),
            password=PasswordConfig(length=128),
            defaults=DefaultsConfig(),
            logging=LoggingConfig()
        )
        gen = PasswordGenerator(config)
        password = gen.generate()

        assert len(password) == 128

    def test_no_charsets_fallback(self):
        """Fallback при отсутствии наборов символов."""
        config = Config(
            user=UserConfig(),
            password=PasswordConfig(
                length=8,
                use_lowercase=False,
                use_uppercase=False,
                use_digits=False,
                use_special=False
            ),
            defaults=DefaultsConfig(),
            logging=LoggingConfig()
        )
        gen = PasswordGenerator(config)
        password = gen.generate()

        assert len(password) == 8
        # Должны использоваться буквы и цифры по умолчанию
        assert any(c in string.ascii_letters for c in password) or any(c in string.digits for c in password)


# =============================================================================
# ТЕСТЫ SPECIAL SYMBOLS
# =============================================================================

class TestPasswordGeneratorSpecialChars:
    """Тесты генерации со спецсимволами."""

    def test_with_special_chars(self):
        """Генерация со спецсимволами."""
        config = Config(
            user=UserConfig(),
            password=PasswordConfig(
                length=16,
                use_lowercase=True,
                use_uppercase=True,
                use_digits=True,
                use_special=True
            ),
            defaults=DefaultsConfig(),
            logging=LoggingConfig()
        )
        gen = PasswordGenerator(config)
        password = gen.generate()

        assert len(password) == 16
        # Проверяем наличие хотя бы одного спецсимвола (не гарантировано, но вероятно)
        # Для надёжности генерируем несколько паролей
        passwords = gen.generate_batch(10)
        has_special = any(
            any(c in string.punctuation for c in pwd)
            for pwd in passwords
        )
        assert has_special is True

    def test_special_chars_only(self):
        """Генерация только со спецсимволами."""
        config = Config(
            user=UserConfig(),
            password=PasswordConfig(
                length=8,
                use_lowercase=False,
                use_uppercase=False,
                use_digits=False,
                use_special=True
            ),
            defaults=DefaultsConfig(),
            logging=LoggingConfig()
        )
        gen = PasswordGenerator(config)
        password = gen.generate()

        assert len(password) == 8
        assert all(c in string.punctuation for c in password)
