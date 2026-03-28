#!/usr/bin/env python3
"""
keycloak_client.py

Фасад для обратной совместимости.

Этот класс предоставляет старый интерфейс для совместимости,
но внутри использует новую архитектуру с протоколами и сервисами.
"""

import logging
import sys
from typing import Any

from keycloak import KeycloakAdmin

from keycloak_userator.config import Config
from keycloak_userator.password import PasswordGenerator
from keycloak_userator.providers import ConcreteKeycloakProvider
from keycloak_userator.services import UserService, UserData


class KeycloakUserGenerator:
    """
    Генератор пользователей в Keycloak (фасад для обратной совместимости).

    Использует новую архитектуру с протоколами и сервисами,
    но сохраняет старый интерфейс для совместимости.
    """

    def __init__(
        self,
        server_url: str,
        username: str,
        password: str,
        config: Config,
        realm_name: str | None = None,
        dry_run: bool = False
    ):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.realm_name = realm_name or config.user.default_realm
        self.config = config
        self.dry_run = dry_run

        # Новая архитектура с внедрением зависимостей
        self._provider = ConcreteKeycloakProvider(
            server_url=self.server_url,
            username=self.username,
            password=self.password,
            realm_name=self.realm_name,
            dry_run=self.dry_run
        )
        self._user_service = UserService(
            keycloak_provider=self._provider,
            config=self.config,
            dry_run=self.dry_run
        )

        # Для обратной совместимости
        self.keycloak_admin: KeycloakAdmin | None = None
        self.stats: dict[str, int] = {
            'created': 0, 'skipped': 0, 'errors': 0, 'total': 0
        }

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('keycloak_user_generator')
        logger.setLevel(getattr(logging, self.config.logging.level))
        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.logging.level))

        file_handler = logging.FileHandler(self.config.logging.file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            self.config.logging.format, datefmt=self.config.logging.date_format
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger

    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = self._setup_logging()
        return self._logger

    def connect(self) -> bool:
        """Подключение к Keycloak."""
        try:
            result = self._provider.connect()
            # Для обратной совместимости сохраняем доступ к KeycloakAdmin
            self.keycloak_admin = self._provider._admin  # type: ignore[assignment]
            return result
        except Exception as e:
            self.logger.error(f"Ошибка подключения к Keycloak: {e}")
            return False

    # =================================================================
    # Методы-обёртки для обратной совместимости с тестами
    # =================================================================

    def _user_exists(self, username: str) -> bool:
        """Обёртка для тестов."""
        return self._provider.user_exists(username)

    def _create_user(
        self,
        username: str,
        password: str,
        email: str,
        first_name: str,
        last_name: str,
        group_id: str | None = None
    ) -> bool:
        """Обёртка для тестов."""
        try:
            # Проверка существования
            if self._user_exists(username):
                self.logger.warning(f"Пользователь '{username}' уже существует - пропускаем")
                self.stats['skipped'] += 1
                return True

            user_id = self._provider.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                group_id=group_id
            )

            if user_id:
                self.logger.debug(f"Пользователь '{username}' создан (ID: {user_id})")
                self.stats['created'] += 1
                return True

            self.stats['errors'] += 1
            return False

        except Exception as e:
            self.logger.error(f"Ошибка создания пользователя '{username}': {e}")
            self.stats['errors'] += 1
            return False

    def _get_or_create_group(self, group_name: str) -> str | None:
        """Обёртка для тестов."""
        try:
            return self._provider.get_or_create_group(group_name)
        except Exception as e:
            self.logger.error(f"Ошибка работы с группой '{group_name}': {e}")
            return None

    def _generate_user_data(self, number: int, password: str) -> dict[str, Any]:
        """Генерация данных пользователя (для тестов)."""
        user = self._user_service._generate_user_data(number, password)
        return {
            'username': user.username,
            'password': user.password,
            'email': user.email,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'enabled': user.enabled,
            'group': user.group_name or ''
        }

    def _log_final_report(self) -> None:
        """Логирование итогового отчёта (для тестов)."""
        self.logger.info("=" * 60)
        self.logger.info("Генерация завершена")
        self.logger.info(f"Всего: {self.stats['total']}")
        self.logger.info(f"Создано: {self.stats['created']}")
        self.logger.info(f"Пропущено (существуют): {self.stats['skipped']}")
        self.logger.info(f"Ошибки: {self.stats['errors']}")
        self.logger.info("=" * 60)

    # =================================================================

    def generate_users(self, count: int, start_number: int) -> list[dict]:
        """Генерация пользователей."""
        # Обновление статистики для обратной совместимости
        users = self._user_service.generate_users(count, start_number)

        # Синхронизация статистики
        service_stats = self._user_service.stats
        self.stats = {
            'created': service_stats.created,
            'skipped': service_stats.skipped,
            'errors': service_stats.errors,
            'total': service_stats.total
        }

        # Конвертация UserData в dict для обратной совместимости
        return [user.to_dict() for user in users]
