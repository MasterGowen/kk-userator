#!/usr/bin/env python3
"""
protocols.py

Протоколы (интерфейсы) для основных компонентов системы.

Использует structural subtyping (PEP 544) для определения интерфейсов.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class KeycloakProvider(Protocol):
    """
    Интерфейс для работы с Keycloak Admin API.

    Абстракция над клиентом Keycloak, позволяющая:
    - Подключаться к серверу
    - Управлять группами
    - Управлять пользователями
    - Проверять существование пользователей
    """

    def connect(self) -> bool:
        """
        Подключение к серверу Keycloak.

        Returns:
            True если подключение успешно, иначе False
        """
        ...

    def get_or_create_group(self, group_name: str) -> str | None:
        """
        Получить или создать группу по имени.

        Args:
            group_name: Имя группы

        Returns:
            ID группы или None если ошибка
        """
        ...

    def user_exists(self, username: str) -> bool:
        """
        Проверить существование пользователя.

        Args:
            username: Имя пользователя

        Returns:
            True если пользователь существует, иначе False
        """
        ...

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        first_name: str,
        last_name: str,
        group_id: str | None = None
    ) -> str | None:
        """
        Создать нового пользователя.

        Args:
            username: Имя пользователя
            password: Пароль
            email: Email
            first_name: Имя
            last_name: Фамилия
            group_id: Опциональный ID группы

        Returns:
            ID созданного пользователя или None если ошибка
        """
        ...


@runtime_checkable
class PasswordGeneratorProtocol(Protocol):
    """
    Интерфейс для генератора паролей.
    """

    def generate(self) -> str:
        """
        Сгенерировать случайный пароль.

        Returns:
            Случайный пароль
        """
        ...

    def generate_batch(self, count: int) -> list[str]:
        """
        Сгенерировать несколько паролей.

        Args:
            count: Количество паролей

        Returns:
            Список сгенерированных паролей
        """
        ...


@runtime_checkable
class CredentialExporterProtocol(Protocol):
    """
    Интерфейс для экспортёра учётных данных.
    """

    def export_csv(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт в CSV формат.

        Args:
            users: Список пользователей
            filename: Опциональное имя файла

        Returns:
            Путь к сохранённому файлу
        """
        ...

    def export_txt(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт в TXT формат.

        Args:
            users: Список пользователей
            filename: Опциональное имя файла

        Returns:
            Путь к сохранённому файлу
        """
        ...

    def export_json(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт в JSON формат.

        Args:
            users: Список пользователей
            filename: Опциональное имя файла

        Returns:
            Путь к сохранённому файлу
        """
        ...


@runtime_checkable
class ConfigProvider(Protocol):
    """
    Интерфейс для поставщика конфигурации.
    """

    @property
    def login_prefix(self) -> str:
        """Префикс для логинов пользователей."""
        ...

    @property
    def email_domain(self) -> str:
        """Домен для email адресов."""
        ...

    @property
    def first_name(self) -> str:
        """Имя по умолчанию."""
        ...

    @property
    def last_name_template(self) -> str:
        """Шаблон фамилии с {number}."""
        ...

    @property
    def group_name(self) -> str:
        """Имя группы для добавления пользователей."""
        ...

    @property
    def password_length(self) -> int:
        """Длина генерируемых паролей."""
        ...
