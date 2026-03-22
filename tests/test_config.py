#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_config.py

Тесты для модуля конфигурации config.py.

Покрывает:
- Валидаторы (validate_login_prefix, validate_email_domain, etc.)
- ConfigLoader (загрузка YAML, переопределение из env)
- Фабричные функции (load_config, get_default_config)
"""

import os
import tempfile

import pytest

from keycloak_userator.config import (
    Config,
    ConfigLoader,
    ConfigValidationError,
    UserConfig,
    PasswordConfig,
    DefaultsConfig,
    LoggingConfig,
    load_config,
    get_default_config,
    validate_login_prefix,
    validate_email_domain,
    validate_password_length,
    validate_last_name_template,
    validate_group_name,
)


# =============================================================================
# ТЕСТЫ ВАЛИДАТОРОВ
# =============================================================================

class TestValidateLoginPrefix:
    """Тесты валидации префикса логинов."""

    def test_valid_prefix_simple(self):
        """Валидный простой префикс."""
        validate_login_prefix("enginc")  # Не должно выбрасывать

    def test_valid_prefix_with_underscore(self):
        """Валидный префикс с подчёркиванием."""
        validate_login_prefix("eng_inc")  # Не должно выбрасывать

    def test_valid_prefix_with_numbers(self):
        """Валидный префикс с цифрами."""
        validate_login_prefix("enginc123")  # Не должно выбрасывать

    def test_valid_prefix_max_length(self):
        """Валидный префикс максимальной длины."""
        validate_login_prefix("a" * 32)  # Не должно выбрасывать

    def test_empty_prefix(self):
        """Пустой префикс."""
        with pytest.raises(ConfigValidationError, match="не может быть пустым"):
            validate_login_prefix("")

    def test_prefix_starts_with_digit(self):
        """Префикс начинается с цифры."""
        with pytest.raises(ConfigValidationError, match="начинаться с буквы"):
            validate_login_prefix("123enginc")

    def test_prefix_cyrillic(self):
        """Префикс с кириллицей."""
        with pytest.raises(ConfigValidationError, match="Недопустимый префикс"):
            validate_login_prefix("инж")

    def test_prefix_too_long(self):
        """Префикс слишком длинный."""
        with pytest.raises(ConfigValidationError, match="слишком длинный"):
            validate_login_prefix("a" * 33)

    def test_prefix_special_chars(self):
        """Префикс со спецсимволами."""
        with pytest.raises(ConfigValidationError, match="Недопустимый префикс"):
            validate_login_prefix("eng-inc")


class TestValidateEmailDomain:
    """Тесты валидации домена email."""

    def test_valid_domain_simple(self):
        """Валидный простой домен."""
        validate_email_domain("urfu.online")  # Не должно выбрасывать

    def test_valid_domain_subdomain(self):
        """Валидный домен с поддоменом."""
        validate_email_domain("mail.urfu.online")  # Не должно выбрасывать

    def test_empty_domain(self):
        """Пустой домен."""
        with pytest.raises(ConfigValidationError, match="не может быть пустым"):
            validate_email_domain("")

    def test_domain_no_dot(self):
        """Домен без точки."""
        with pytest.raises(ConfigValidationError, match="хотя бы одну точку"):
            validate_email_domain("urfu")

    def test_domain_special_chars(self):
        """Домен со спецсимволами."""
        with pytest.raises(ConfigValidationError, match="Недопустимый домен"):
            validate_email_domain("urfu.online@")


class TestValidatePasswordLength:
    """Тесты валидации длины пароля."""

    def test_valid_length_min(self):
        """Минимальная допустимая длина."""
        validate_password_length(6)  # Не должно выбрасывать

    def test_valid_length_default(self):
        """Длина по умолчанию."""
        validate_password_length(8)  # Не должно выбрасывать

    def test_valid_length_max(self):
        """Максимальная допустимая длина."""
        validate_password_length(128)  # Не должно выбрасывать

    def test_length_too_short(self):
        """Длина слишком маленькая."""
        with pytest.raises(ConfigValidationError, match="слишком мала"):
            validate_password_length(5)

    def test_length_too_long(self):
        """Длина слишком большая."""
        with pytest.raises(ConfigValidationError, match="слишком велика"):
            validate_password_length(129)

    def test_length_zero(self):
        """Нулевая длина."""
        with pytest.raises(ConfigValidationError, match="слишком мала"):
            validate_password_length(0)


class TestValidateLastNameTemplate:
    """Тесты валидации шаблона фамилии."""

    def test_valid_template(self):
        """Валидный шаблон."""
        validate_last_name_template("Студентов {number}")  # Не должно выбрасывать

    def test_valid_template_complex(self):
        """Валидный сложный шаблон."""
        validate_last_name_template("User_{number}_Test")  # Не должно выбрасывать

    def test_empty_template(self):
        """Пустой шаблон."""
        with pytest.raises(ConfigValidationError, match="не может быть пустым"):
            validate_last_name_template("")

    def test_template_no_number_placeholder(self):
        """Шаблон без {number}."""
        with pytest.raises(ConfigValidationError, match="{number}"):
            validate_last_name_template("Студентов")

    def test_template_wrong_placeholder(self):
        """Шаблон с другим плейсхолдером."""
        with pytest.raises(ConfigValidationError, match="{number}"):
            validate_last_name_template("Студентов {id}")


class TestValidateGroupName:
    """Тесты валидации имени группы."""

    def test_valid_name(self):
        """Валидное имя группы."""
        validate_group_name("engforinclusb-users")  # Не должно выбрасывать

    def test_valid_name_max_length(self):
        """Имя группы максимальной длины."""
        validate_group_name("a" * 64)  # Не должно выбрасывать

    def test_empty_name(self):
        """Пустое имя группы."""
        with pytest.raises(ConfigValidationError, match="не может быть пустым"):
            validate_group_name("")

    def test_name_too_long(self):
        """Имя группы слишком длинное."""
        with pytest.raises(ConfigValidationError, match="слишком длинное"):
            validate_group_name("a" * 65)


# =============================================================================
# ТЕСТЫ CONFIGLOADER
# =============================================================================

class TestConfigLoader:
    """Тесты загрузчика конфигурации."""

    def test_load_default_config(self):
        """Загрузка конфигурации по умолчанию (пустой файл)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("{}")
            f.flush()
            try:
                loader = ConfigLoader(f.name)
                config = loader.load()

                assert config.user.login_prefix == "enginc"
                assert config.user.email_domain == "urfu.online"
                assert config.password.length == 8
                assert config.defaults.count == 200
                assert config.logging.level == "INFO"
            finally:
                os.unlink(f.name)

    def test_load_custom_config(self):
        """Загрузка пользовательской конфигурации."""
        config_yaml = """
user:
  login_prefix: "testuser"
  email_domain: "example.com"
  first_name: "Тест"
  last_name_template: "Тестов {number}"
  group_name: "test-group"

password:
  length: 12
  use_lowercase: true
  use_uppercase: true
  use_digits: true
  use_special: false

defaults:
  count: 50
  start_number: 10
  output_dir: "test_output"

logging:
  level: "DEBUG"
  file: "test.log"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            f.flush()
            try:
                loader = ConfigLoader(f.name)
                config = loader.load()

                assert config.user.login_prefix == "testuser"
                assert config.user.email_domain == "example.com"
                assert config.user.first_name == "Тест"
                assert config.password.length == 12
                assert config.defaults.count == 50
                assert config.defaults.start_number == 10
                assert config.logging.level == "DEBUG"
            finally:
                os.unlink(f.name)

    def test_load_env_override(self):
        """Переопределение из переменных окружения."""
        config_yaml = "{}"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            f.flush()
            try:
                # Устанавливаем переменные окружения
                os.environ['KEYCLOAK_LOGIN_PREFIX'] = 'envprefix'
                os.environ['KEYCLOAK_EMAIL_DOMAIN'] = 'env.example.com'
                os.environ['KEYCLOAK_COUNT'] = '999'
                os.environ['KEYCLOAK_OUTPUT_DIR'] = 'env_output'

                loader = ConfigLoader(f.name)
                config = loader.load()

                assert config.user.login_prefix == 'envprefix'
                assert config.user.email_domain == 'env.example.com'
                assert config.defaults.count == 999
                assert config.defaults.output_dir == 'env_output'
            finally:
                os.unlink(f.name)
                # Очищаем переменные окружения
                os.environ.pop('KEYCLOAK_LOGIN_PREFIX', None)
                os.environ.pop('KEYCLOAK_EMAIL_DOMAIN', None)
                os.environ.pop('KEYCLOAK_COUNT', None)
                os.environ.pop('KEYCLOAK_OUTPUT_DIR', None)

    def test_load_nonexistent_file(self):
        """Загрузка несуществующего файла."""
        loader = ConfigLoader("/nonexistent/path/config.yaml")
        config = loader.load()  # Должен вернуть дефолтную конфигурацию

        assert config.user.login_prefix == "enginc"
        assert config.config_path == "/nonexistent/path/config.yaml"

    def test_validation_error_on_load(self):
        """Ошибка валидации при загрузке."""
        config_yaml = """
user:
  login_prefix: "123invalid"  # Начинается с цифры
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            f.flush()
            try:
                loader = ConfigLoader(f.name)
                with pytest.raises(ConfigValidationError, match="начинаться с буквы"):
                    loader.load()
            finally:
                os.unlink(f.name)


# =============================================================================
# ТЕСТЫ ФАБРИЧНЫХ ФУНКЦИЙ
# =============================================================================

class TestFactoryFunctions:
    """Тесты фабричных функций."""

    def test_get_default_config(self):
        """Получение конфигурации по умолчанию."""
        config = get_default_config()

        assert isinstance(config, Config)
        assert config.user.login_prefix == "enginc"
        assert config.password.length == 8
        assert config.defaults.count == 200
        assert config.logging.level == "INFO"

    def test_load_config_with_path(self):
        """Загрузка конфигурации с указанием пути."""
        config_yaml = """
user:
  login_prefix: "custom"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_yaml)
            f.flush()
            try:
                config = load_config(f.name)
                assert config.user.login_prefix == "custom"
            finally:
                os.unlink(f.name)


# =============================================================================
# ТЕСТЫ DATACLASS
# =============================================================================

class TestDataClasses:
    """Тесты классов данных."""

    def test_user_config_default(self):
        """UserConfig со значениями по умолчанию."""
        config = UserConfig()

        assert config.login_prefix == "enginc"
        assert config.email_domain == "urfu.online"
        assert config.first_name == "Студент"
        assert config.group_name == "engforinclusb-users"

    def test_user_config_custom(self):
        """UserConfig с пользовательскими значениями."""
        config = UserConfig(
            login_prefix="test",
            email_domain="test.com",
            first_name="Тест",
            last_name_template="Тестов {number}",
            group_name="test-group",
            default_realm="test-realm"
        )

        assert config.login_prefix == "test"
        assert config.email_domain == "test.com"
        assert config.first_name == "Тест"
        assert config.group_name == "test-group"

    def test_password_config_default(self):
        """PasswordConfig со значениями по умолчанию."""
        config = PasswordConfig()

        assert config.length == 8
        assert config.use_lowercase is True
        assert config.use_uppercase is True
        assert config.use_digits is True
        assert config.use_special is False

    def test_password_config_custom(self):
        """PasswordConfig с пользовательскими значениями."""
        config = PasswordConfig(
            length=16,
            use_lowercase=True,
            use_uppercase=False,
            use_digits=True,
            use_special=True
        )

        assert config.length == 16
        assert config.use_lowercase is True
        assert config.use_uppercase is False
        assert config.use_digits is True
        assert config.use_special is True

    def test_defaults_config(self):
        """DefaultsConfig."""
        config = DefaultsConfig()

        assert config.count == 200
        assert config.start_number == 1
        assert config.output_dir == "output"

    def test_logging_config(self):
        """LoggingConfig."""
        config = LoggingConfig()

        assert config.file == "keycloak_generator.log"
        assert config.level == "INFO"
        assert "%(asctime)s" in config.format
