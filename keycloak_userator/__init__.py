#!/usr/bin/env python3
"""
keycloak_userator

Пакет для массового создания пользователей в Keycloak.

Версия: 2.0.0
"""

__version__ = '2.0.0'
__author__ = 'kk-userator project'

# Экспорт основных классов
from keycloak_userator.config import Config, ConfigValidationError, load_config
from keycloak_userator.exporter import CredentialExporter
from keycloak_userator.keycloak_client import KeycloakUserGenerator
from keycloak_userator.password import PasswordGenerator
from keycloak_userator.types import (
    ConnectionConfig,
    CredentialDict,
    GenerationStats,
    NewUserDict,
    UserCredentials,
    UserData,
)

__all__ = [
    'PasswordGenerator',
    'CredentialExporter',
    'KeycloakUserGenerator',
    'Config',
    'load_config',
    'ConfigValidationError',
    'UserData',
    'UserCredentials',
    'ConnectionConfig',
    'GenerationStats',
    'NewUserDict',
    'CredentialDict',
]
