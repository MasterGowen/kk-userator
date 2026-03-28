#!/usr/bin/env python3
"""
keycloak_client.py — Клиент для работы с Keycloak Admin API.
"""

import logging
import sys
from typing import Any

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

from keycloak_userator.config import Config
from keycloak_userator.password import PasswordGenerator


class KeycloakUserGenerator:
    """Генератор пользователей в Keycloak."""

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
        try:
            self.logger.info(f"Подключение к Keycloak: {self.server_url}")
            self.logger.info(f"Realm: {self.realm_name}")

            if self.dry_run:
                self.logger.warning("РЕЖИМ DRY-RUN: реальные операции не выполняются")
                return True

            self.keycloak_admin = KeycloakAdmin(
                server_url=f"{self.server_url}/",
                username=self.username,
                password=self.password,
                realm_name=self.realm_name,
                verify=True
            )

            realm_info = self.keycloak_admin.get_realm(self.realm_name)
            self.logger.info(f"Успешное подключение к realm: {realm_info.get('realm', 'unknown')}")
            return True

        except (KeycloakError, Exception) as e:
            self.logger.error(f"Ошибка подключения к Keycloak: {e}")
            return False

    def _get_or_create_group(self, group_name: str) -> str | None:
        try:
            assert self.keycloak_admin is not None, "KeycloakAdmin not initialized"  # nosec B101
            existing_groups = self.keycloak_admin.get_groups(query={"search": group_name})

            for group in existing_groups:
                if group.get('name') == group_name:
                    group_id = group.get('id')
                    self.logger.info(f"Группа '{group_name}' уже существует (ID: {group_id})")
                    return group_id  # type: ignore[no-any-return]

            self.logger.info(f"Создание группы '{group_name}'")
            group_id = self.keycloak_admin.create_group({'name': group_name})
            self.logger.info(f"Группа создана (ID: {group_id})")
            return group_id

        except KeycloakError as e:
            self.logger.error(f"Ошибка при работе с группой: {e}")
            return None

    def _user_exists(self, username: str) -> bool:
        try:
            assert self.keycloak_admin is not None, "KeycloakAdmin not initialized"  # nosec B101
            users = self.keycloak_admin.get_users(query={"search": username})
            return any(user.get('username') == username for user in users)
        except KeycloakError:
            return False

    def _create_user(
        self, username: str, password: str, email: str,
        first_name: str, last_name: str, group_id: str | None = None
    ) -> bool:
        try:
            if self._user_exists(username):
                self.logger.warning(f"Пользователь '{username}' уже существует - пропускаем")
                self.stats['skipped'] += 1
                return True

            new_user: dict[str, Any] = {
                'username': username, 'email': email,
                'firstName': first_name, 'lastName': last_name,
                'enabled': True, 'emailVerified': False,
                'credentials': [{'type': 'password', 'value': password, 'temporary': False}]
            }

            assert self.keycloak_admin is not None, "KeycloakAdmin not initialized"  # nosec B101
            user_id = self.keycloak_admin.create_user(new_user)
            self.logger.debug(f"Пользователь '{username}' создан (ID: {user_id})")

            if group_id:
                self.keycloak_admin.group_user_add(user_id=user_id, group_id=group_id)
                self.logger.debug(f"Пользователь '{username}' добавлен в группу")

            self.stats['created'] += 1
            return True

        except (KeycloakError, Exception) as e:
            self.logger.error(f"Ошибка создания пользователя '{username}': {e}")
            self.stats['errors'] += 1
            return False

    def _generate_user_data(self, number: int, password: str) -> dict[str, Any]:
        username = f"{self.config.user.login_prefix}_{number}"
        email = f"{self.config.user.login_prefix}_{number}@{self.config.user.email_domain}"
        last_name = self.config.user.last_name_template.format(number=number)

        return {
            'username': username, 'password': password, 'email': email,
            'firstName': self.config.user.first_name, 'lastName': last_name,
            'enabled': True, 'group': self.config.user.group_name
        }

    def generate_users(self, count: int, start_number: int) -> list[dict[str, Any]]:
        self.stats['total'] = count
        created_users = []
        password_gen = PasswordGenerator(self.config)

        self.logger.info(f"Начало генерации {count} пользователей (начиная с {start_number})")

        group_id = None
        if not self.dry_run and self.keycloak_admin:
            group_id = self._get_or_create_group(self.config.user.group_name)
            if group_id:
                self.logger.info(f"Все пользователи будут добавлены в группу '{self.config.user.group_name}'")

        for i in range(start_number, start_number + count):
            password = password_gen.generate()
            user_data = self._generate_user_data(i, password)

            if self.dry_run:
                self.logger.info(f"[DRY-RUN] Будет создан: {user_data['username']} | {user_data['email']}")
                created_users.append(user_data)
                self.stats['created'] += 1
            else:
                if self._create_user(
                    user_data['username'], password, user_data['email'],
                    user_data['firstName'], user_data['lastName'], group_id
                ):
                    created_users.append(user_data)
                    self.logger.info(f"Создан: {user_data['username']} | {user_data['email']}")
                else:
                    self.logger.error(f"Не удалось создать: {user_data['username']}")

            if not self.dry_run and i % 10 == 0:
                self.logger.info(f"Прогресс: {i - start_number + 1}/{count}")

        self._log_final_report()
        return created_users

    def _log_final_report(self) -> None:
        self.logger.info("=" * 60)
        self.logger.info("Генерация завершена")
        self.logger.info(f"Всего: {self.stats['total']}")
        self.logger.info(f"Создано: {self.stats['created']}")
        self.logger.info(f"Пропущено (существуют): {self.stats['skipped']}")
        self.logger.info(f"Ошибки: {self.stats['errors']}")
        self.logger.info("=" * 60)
