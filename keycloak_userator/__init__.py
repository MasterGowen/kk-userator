#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
keycloak_userator

Пакет для массового создания пользователей в Keycloak.

Версия: 2.0.0
"""

__version__ = '2.0.0'
__author__ = 'kk-userator project'

# Экспорт основных классов
from keycloak_userator.password import PasswordGenerator
from keycloak_userator.exporter import CredentialExporter
from keycloak_userator.keycloak_client import KeycloakUserGenerator
from keycloak_userator.config import Config, load_config, ConfigValidationError
from keycloak_userator.types import (
    UserData,
    UserCredentials,
    ConnectionConfig,
    GenerationStats,
    NewUserDict,
    CredentialDict,
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
