#!/usr/bin/env python3
"""
keycloak_userator

Пакет для массового создания пользователей в Keycloak.

Версия: 2.0.0

Архитектура:
- protocols.py — протоколы (интерфейсы) компонентов
- providers.py — реализации провайдеров (ConcreteKeycloakProvider)
- services.py — сервисный слой с бизнес-логикой (UserService)
- exceptions.py — иерархия исключений
- keycloak_client.py — фасад для обратной совместимости
"""

__version__ = '2.0.0'
__author__ = 'kk-userator project'

# Экспорт основных классов
from keycloak_userator.config import Config, ConfigValidationError, load_config
from keycloak_userator.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConnectionError,
    ExportError,
    GroupOperationError,
    UseratorError,
    UserCreationError,
    ValidationError,
)
from keycloak_userator.exporter import CredentialExporter
from keycloak_userator.keycloak_client import KeycloakUserGenerator
from keycloak_userator.password import PasswordGenerator
from keycloak_userator.protocols import (
    ConfigProvider,
    CredentialExporterProtocol,
    KeycloakProvider,
    PasswordGeneratorProtocol,
)
from keycloak_userator.providers import ConcreteKeycloakProvider
from keycloak_userator.services import GenerationStats, UserData, UserService
from keycloak_userator.types import (
    ConnectionConfig,
    CredentialDict,
    NewUserDict,
    UserCredentials,
)

__all__ = [
    # Версия
    '__version__',

    # Фасад (обратная совместимость)
    'KeycloakUserGenerator',

    # Конфигурация
    'Config',
    'load_config',
    'ConfigValidationError',

    # Протоколы (интерфейсы)
    'KeycloakProvider',
    'PasswordGeneratorProtocol',
    'CredentialExporterProtocol',
    'ConfigProvider',

    # Реализации провайдеров
    'ConcreteKeycloakProvider',

    # Сервисы
    'UserService',
    'UserData',
    'GenerationStats',

    # Компоненты
    'PasswordGenerator',
    'CredentialExporter',

    # Типы (TypedDict)
    'UserData',
    'UserCredentials',
    'ConnectionConfig',
    'NewUserDict',
    'CredentialDict',

    # Исключения
    'UseratorError',
    'ConfigurationError',
    'ConnectionError',
    'AuthenticationError',
    'AuthorizationError',
    'UserCreationError',
    'GroupOperationError',
    'ExportError',
    'ValidationError',
]
