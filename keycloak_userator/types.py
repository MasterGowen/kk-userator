#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
types.py

Типизированные структуры данных для генератора пользователей Keycloak.

Содержит:
- TypedDict для данных пользователей
- Структуры для конфигурации подключения
- Статистика операций
"""

from typing import Any, Dict, TypedDict


class UserData(TypedDict):
    """
    Структура данных пользователя.

    Attributes:
        username: Имя пользователя (логин)
        password: Пароль
        email: Email адрес
        firstName: Имя
        lastName: Фамилия
        enabled: Статус учётной записи
        group: Имя группы
    """
    username: str
    password: str
    email: str
    firstName: str
    lastName: str
    enabled: bool
    group: str


class UserCredentials(TypedDict):
    """
    Структура учётных данных для подключения.

    Attributes:
        server_url: URL сервера Keycloak
        username: Имя пользователя администратора
        password: Пароль администратора
        realm: Имя realm
    """
    server_url: str
    username: str
    password: str
    realm: str


class ConnectionConfig(TypedDict, total=False):
    """
    Конфигурация подключения к Keycloak.

    Attributes:
        server_url: URL сервера
        username: Логин администратора
        password: Пароль администратора
        realm_name: Имя realm
        verify: Проверка SSL сертификата
    """
    server_url: str
    username: str
    password: str
    realm_name: str
    verify: bool


class GenerationStats(TypedDict):
    """
    Статистика генерации пользователей.

    Attributes:
        created: Количество созданных пользователей
        skipped: Количество пропущенных (существующих)
        errors: Количество ошибок
        total: Общее количество запланированных
    """
    created: int
    skipped: int
    errors: int
    total: int


class NewUserDict(TypedDict):
    """
    Структура для создания пользователя в Keycloak API.

    Attributes:
        username: Имя пользователя
        email: Email адрес
        firstName: Имя
        lastName: Фамилия
        enabled: Статус
        emailVerified: Статус подтверждения email
        credentials: Список учётных данных
    """
    username: str
    email: str
    firstName: str
    lastName: str
    enabled: bool
    emailVerified: bool
    credentials: list[Dict[str, Any]]


class CredentialDict(TypedDict):
    """
    Структура учётных данных для Keycloak.

    Attributes:
        type: Тип учётных данных (password)
        value: Значение (пароль)
        temporary: Временный ли пароль
    """
    type: str
    value: str
    temporary: bool
