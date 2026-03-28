#!/usr/bin/env python3
"""
config.py

Модуль конфигурации для генератора пользователей Keycloak.

Обеспечивает:
- Загрузку конфигурации из YAML-файла
- Переопределение параметров через переменные окружения
- Валидацию параметров
- Централизованное управление настройками
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Ошибка: не установлена библиотека PyYAML")
    print("Установите зависимости: pip install -r requirements.txt")
    raise


# =============================================================================
# КОНСТАНТЫ
# =============================================================================

DEFAULT_CONFIG_FILE = "config.yaml"
CONFIG_ENV_VAR = "KEYCLOAK_CONFIG"


# =============================================================================
# КЛАССЫ ДАННЫХ
# =============================================================================

@dataclass
class UserConfig:
    """Конфигурация параметров пользователей."""
    login_prefix: str = "enginc"
    email_domain: str = "urfu.online"
    first_name: str = "Студент"
    last_name_template: str = "Студентов {number}"
    group_name: str = "engforinclusb-users"
    default_realm: str = "master"


@dataclass
class PasswordConfig:
    """Конфигурация генерации паролей."""
    length: int = 8
    use_lowercase: bool = True
    use_uppercase: bool = True
    use_digits: bool = True
    use_special: bool = False


@dataclass
class DefaultsConfig:
    """Параметры по умолчанию."""
    count: int = 200
    start_number: int = 1
    output_dir: str = "output"


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""
    file: str = "keycloak_generator.log"
    level: str = "INFO"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class Config:
    """
    Основная конфигурация приложения.

    Объединяет все секции конфигурации в единый объект.
    """
    user: UserConfig = field(default_factory=UserConfig)
    password: PasswordConfig = field(default_factory=PasswordConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Путь к файлу конфигурации
    config_path: str | None = None


# =============================================================================
# ВАЛИДАТОРЫ
# =============================================================================

class ConfigValidationError(Exception):
    """Исключение ошибки валидации конфигурации."""
    pass


def validate_login_prefix(prefix: str) -> None:
    """
    Валидация префикса для логинов.

    Требования:
    - Только латинские буквы, цифры и подчёркивание
    - Не должен начинаться с цифры
    - Длина от 1 до 32 символов

    Args:
        prefix: Префикс для проверки

    Raises:
        ConfigValidationError: Если префикс невалиден
    """
    if not prefix:
        raise ConfigValidationError("Префикс логинов не может быть пустым")

    if len(prefix) > 32:
        raise ConfigValidationError(
            f"Префикс логинов слишком длинный (макс. 32 символа): {len(prefix)}"
        )

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', prefix):
        raise ConfigValidationError(
            f"Недопустимый префикс логинов: '{prefix}'. "
            "Допускаются только латинские буквы, цифры и подчёркивание. "
            "Префикс должен начинаться с буквы."
        )


def validate_email_domain(domain: str) -> None:
    """
    Валидация домена email.

    Требования:
    - Не пустой
    - Содержит хотя бы одну точку
    - Состоит из допустимых символов

    Args:
        domain: Домен для проверки

    Raises:
        ConfigValidationError: Если домен невалиден
    """
    if not domain:
        raise ConfigValidationError("Домен email не может быть пустым")

    if '.' not in domain:
        raise ConfigValidationError(
            f"Домен email должен содержать хотя бы одну точку: '{domain}'"
        )

    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
        raise ConfigValidationError(
            f"Недопустимый домен email: '{domain}'"
        )


def validate_password_length(length: int) -> None:
    """
    Валидация длины пароля.

    Args:
        length: Длина пароля для проверки

    Raises:
        ConfigValidationError: Если длина невалидна
    """
    if length < 6:
        raise ConfigValidationError(
            f"Длина пароля слишком мала (мин. 6 символов): {length}"
        )

    if length > 128:
        raise ConfigValidationError(
            f"Длина пароля слишком велика (макс. 128 символов): {length}"
        )


def validate_last_name_template(template: str) -> None:
    """
    Валидация шаблона фамилии.

    Args:
        template: Шаблон для проверки

    Raises:
        ConfigValidationError: Если шаблон невалиден
    """
    if not template:
        raise ConfigValidationError("Шаблон фамилии не может быть пустым")

    if '{number}' not in template:
        raise ConfigValidationError(
            f"Шаблон фамилии должен содержать '{{number}}': '{template}'"
        )


def validate_group_name(name: str) -> None:
    """
    Валидация имени группы.

    Args:
        name: Имя группы для проверки

    Raises:
        ConfigValidationError: Если имя группы невалидно
    """
    if not name:
        raise ConfigValidationError("Имя группы не может быть пустым")

    if len(name) > 64:
        raise ConfigValidationError(
            f"Имя группы слишком длинное (макс. 64 символа): {len(name)}"
        )


# =============================================================================
# ЗАГРУЗЧИК КОНФИГУРАЦИИ
# =============================================================================

class ConfigLoader:
    """
    Загрузчик конфигурации из YAML-файла.

    Поддерживает:
    - Загрузку из файла
    - Переопределение через переменные окружения
    - Валидацию параметров
    """

    def __init__(self, config_path: str | None = None):
        """
        Инициализация загрузчика.

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path or self._get_config_path()

    def _get_config_path(self) -> str:
        """
        Получение пути к файлу конфигурации.

        Приоритет:
        1. Переменная окружения KEYCLOAK_CONFIG
        2. Путь по умолчанию (config.yaml)

        Returns:
            Путь к файлу конфигурации
        """
        env_path = os.environ.get(CONFIG_ENV_VAR)
        if env_path:
            return env_path
        return DEFAULT_CONFIG_FILE

    def load(self) -> Config:
        """
        Загрузка конфигурации из файла.

        Returns:
            Объект конфигурации

        Raises:
            FileNotFoundError: Если файл конфигурации не найден
            ConfigValidationError: Если конфигурация невалидна
        """
        config_data = self._load_yaml()
        config = self._parse_config(config_data)
        self._validate_config(config)
        return config

    def _load_yaml(self) -> dict:
        """
        Загрузка YAML-файла.

        Returns:
            Словарь с данными конфигурации

        Raises:
            FileNotFoundError: Если файл не найден
        """
        config_path = Path(self.config_path)

        if not config_path.exists():
            return {}

        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data else {}

    def _parse_config(self, data: dict) -> Config:
        """
        Парсинг данных конфигурации.

        Args:
            data: Словарь с данными

        Returns:
            Объект конфигурации
        """
        user_data = data.get('user', {})
        user_config = UserConfig(
            login_prefix=user_data.get('login_prefix', UserConfig.login_prefix),
            email_domain=user_data.get('email_domain', UserConfig.email_domain),
            first_name=user_data.get('first_name', UserConfig.first_name),
            last_name_template=user_data.get('last_name_template', UserConfig.last_name_template),
            group_name=user_data.get('group_name', UserConfig.group_name),
            default_realm=user_data.get('default_realm', UserConfig.default_realm),
        )

        env_login_prefix = os.environ.get('KEYCLOAK_LOGIN_PREFIX')
        if env_login_prefix:
            user_config.login_prefix = env_login_prefix

        env_email_domain = os.environ.get('KEYCLOAK_EMAIL_DOMAIN')
        if env_email_domain:
            user_config.email_domain = env_email_domain

        password_data = data.get('password', {})
        password_config = PasswordConfig(
            length=password_data.get('length', PasswordConfig.length),
            use_lowercase=password_data.get('use_lowercase', PasswordConfig.use_lowercase),
            use_uppercase=password_data.get('use_uppercase', PasswordConfig.use_uppercase),
            use_digits=password_data.get('use_digits', PasswordConfig.use_digits),
            use_special=password_data.get('use_special', PasswordConfig.use_special),
        )

        defaults_data = data.get('defaults', {})
        defaults_config = DefaultsConfig(
            count=defaults_data.get('count', DefaultsConfig.count),
            start_number=defaults_data.get('start_number', DefaultsConfig.start_number),
            output_dir=defaults_data.get('output_dir', DefaultsConfig.output_dir),
        )

        env_count = os.environ.get('KEYCLOAK_COUNT')
        if env_count:
            defaults_config.count = int(env_count)

        env_output_dir = os.environ.get('KEYCLOAK_OUTPUT_DIR')
        if env_output_dir:
            defaults_config.output_dir = env_output_dir

        logging_data = data.get('logging', {})
        logging_config = LoggingConfig(
            file=logging_data.get('file', LoggingConfig.file),
            level=logging_data.get('level', LoggingConfig.level),
            format=logging_data.get('format', LoggingConfig.format),
            date_format=logging_data.get('date_format', LoggingConfig.date_format),
        )

        return Config(
            user=user_config,
            password=password_config,
            defaults=defaults_config,
            logging=logging_config,
            config_path=self.config_path,
        )

    def _validate_config(self, config: Config) -> None:
        """
        Валидация конфигурации.

        Args:
            config: Объект конфигурации для проверки

        Raises:
            ConfigValidationError: Если конфигурация невалидна
        """
        validate_login_prefix(config.user.login_prefix)
        validate_email_domain(config.user.email_domain)
        validate_password_length(config.password.length)
        validate_last_name_template(config.user.last_name_template)
        validate_group_name(config.user.group_name)


# =============================================================================
# УТИЛИТЫ
# =============================================================================

def load_config(config_path: str | None = None) -> Config:
    """
    Загрузка конфигурации.

    Convenience-функция для быстрой загрузки конфигурации.

    Args:
        config_path: Путь к файлу конфигурации (опционально)

    Returns:
        Объект конфигурации
    """
    loader = ConfigLoader(config_path)
    return loader.load()


def get_default_config() -> Config:
    """
    Получение конфигурации по умолчанию.

    Returns:
        Конфигурация со значениями по умолчанию
    """
    return Config()
