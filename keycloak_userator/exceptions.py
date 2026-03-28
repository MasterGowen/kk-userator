#!/usr/bin/env python3
"""
exceptions.py

Иерархия исключений для генератора пользователей Keycloak.
"""


class UseratorError(Exception):
    """Базовое исключение для всех ошибок генератора."""

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConfigurationError(UseratorError):
    """Ошибка конфигурации (неверные параметры, отсутствующие файлы)."""
    pass


class ConnectionError(UseratorError):
    """Ошибка подключения к Keycloak."""
    pass


class AuthenticationError(UseratorError):
    """Ошибка аутентификации (неверные учётные данные)."""
    pass


class AuthorizationError(UseratorError):
    """Ошибка авторизации (недостаточно прав)."""
    pass


class UserCreationError(UseratorError):
    """Ошибка создания пользователя."""

    def __init__(self, username: str, message: str, details: str | None = None):
        super().__init__(message, details)
        self.username = username


class GroupOperationError(UseratorError):
    """Ошибка операции с группой."""

    def __init__(self, group_name: str, message: str, details: str | None = None):
        super().__init__(message, details)
        self.group_name = group_name


class ExportError(UseratorError):
    """Ошибка экспорта данных."""

    def __init__(self, format_type: str, message: str, details: str | None = None):
        super().__init__(message, details)
        self.format_type = format_type


class ValidationError(UseratorError):
    """Ошибка валидации данных."""

    def __init__(self, field: str, message: str, details: str | None = None):
        super().__init__(message, details)
        self.field = field
