#!/usr/bin/env python3
"""
services.py

Сервисный слой с бизнес-логикой.

Здесь находится основная логика генерации пользователей,
оркестрирующая взаимодействие с провайдерами.
"""

import logging
from dataclasses import dataclass
from typing import Any

from keycloak_userator.config import Config
from keycloak_userator.password import PasswordGenerator
from keycloak_userator.protocols import KeycloakProvider


@dataclass
class GenerationStats:
    """Статистика генерации пользователей."""

    created: int = 0
    skipped: int = 0
    errors: int = 0
    total: int = 0

    @property
    def success_rate(self) -> float:
        """Процент успешных операций."""
        if self.total == 0:
            return 0.0
        return (self.created / self.total) * 100


@dataclass
class UserData:
    """Модель данных пользователя."""

    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    enabled: bool = True
    group_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Конвертация в словарь для экспорта."""
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'enabled': self.enabled,
            'group': self.group_name or ''
        }


class UserService:
    """
    Сервис для генерации и управления пользователями.

    Реализует бизнес-логику создания пакетов пользователей,
    используя абстракции (протоколы) для внешних зависимостей.

    Принцип инверсии зависимостей:
    - Зависит от абстракции KeycloakProvider, а не реализации
    - Зависимости внедряются через конструктор (DI)
    """

    def __init__(
        self,
        keycloak_provider: KeycloakProvider,
        config: Config,
        dry_run: bool = False
    ):
        """
        Инициализация сервиса пользователей.

        Args:
            keycloak_provider: Провайдер для работы с Keycloak (абстракция)
            config: Конфигурация приложения
            dry_run: Режим сухой проверки
        """
        self._keycloak = keycloak_provider
        self._config = config
        self._dry_run = dry_run
        self._stats = GenerationStats()
        self._logger = logging.getLogger(__name__)

    @property
    def stats(self) -> GenerationStats:
        """Получить статистику операций."""
        return self._stats

    @property
    def logger(self) -> logging.Logger:
        """Получить логгер."""
        return self._logger

    def _generate_user_data(self, number: int, password: str) -> UserData:
        """
        Генерация данных пользователя на основе номера и пароля.

        Args:
            number: Порядковый номер пользователя
            password: Сгенерированный пароль

        Returns:
            Модель UserData с данными пользователя
        """
        prefix = self._config.user.login_prefix
        username = f"{prefix}_{number}"
        email = f"{prefix}_{number}@{self._config.user.email_domain}"
        last_name = self._config.user.last_name_template.format(number=number)

        return UserData(
            username=username,
            password=password,
            email=email,
            first_name=self._config.user.first_name,
            last_name=last_name,
            enabled=True,
            group_name=self._config.user.group_name
        )

    def _create_user(self, user: UserData, group_id: str | None) -> bool:
        """
        Создание одного пользователя.

        Args:
            user: Модель пользователя
            group_id: ID группы для добавления

        Returns:
            True если пользователь создан или уже существует, иначе False
        """
        try:
            # Проверка существования
            if self._keycloak.user_exists(user.username):
                self._logger.warning(
                    f"Пользователь '{user.username}' уже существует - пропускаем"
                )
                self._stats.skipped += 1
                return True

            # Создание пользователя
            user_id = self._keycloak.create_user(
                username=user.username,
                password=user.password,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                group_id=group_id
            )

            if user_id:
                self._logger.debug(f"Пользователь '{user.username}' создан (ID: {user_id})")
                self._stats.created += 1
                return True

            self._stats.errors += 1
            return False

        except Exception as e:
            self._logger.error(f"Ошибка создания '{user.username}': {e}")
            self._stats.errors += 1
            return False

    def generate_users(
        self,
        count: int,
        start_number: int = 1
    ) -> list[UserData]:
        """
        Генерация пакета пользователей.

        Args:
            count: Количество пользователей для создания
            start_number: Начальный номер нумерации

        Returns:
            Список созданных пользователей
        """
        self._stats = GenerationStats(total=count)
        created_users: list[UserData] = []
        password_gen = PasswordGenerator(self._config)

        self._logger.info(
            f"Начало генерации {count} пользователей (начиная с {start_number})"
        )

        # Получение или создание группы
        group_id: str | None = None
        if not self._dry_run:
            group_id = self._keycloak.get_or_create_group(
                self._config.user.group_name
            )
            if group_id:
                self._logger.info(
                    f"Все пользователи будут добавлены в группу "
                    f"'{self._config.user.group_name}'"
                )

        # Генерация пользователей
        for i in range(start_number, start_number + count):
            password = password_gen.generate()
            user = self._generate_user_data(i, password)

            if self._dry_run:
                self._logger.info(
                    f"[DRY-RUN] Будет создан: {user.username} | {user.email}"
                )
                created_users.append(user)
                self._stats.created += 1
            else:
                if self._create_user(user, group_id):
                    created_users.append(user)
                    self._logger.info(
                        f"Создан: {user.username} | {user.email}"
                    )
                else:
                    self._logger.error(f"Не удалось создать: {user.username}")

            # Прогресс каждые 10 пользователей
            if not self._dry_run and i % 10 == 0:
                progress = i - start_number + 1
                self._logger.info(f"Прогресс: {progress}/{count}")

        self._log_final_report()
        return created_users

    def _log_final_report(self) -> None:
        """Логирование итогового отчёта."""
        self._logger.info("=" * 60)
        self._logger.info("Генерация завершена")
        self._logger.info(f"Всего: {self._stats.total}")
        self._logger.info(f"Создано: {self._stats.created}")
        self._logger.info(f"Пропущено: {self._stats.skipped}")
        self._logger.info(f"Ошибки: {self._stats.errors}")
        self._logger.info(f"Успешность: {self._stats.success_rate:.1f}%")
        self._logger.info("=" * 60)
