#!/usr/bin/env python3
"""
providers.py

Реализации провайдеров для работы с внешними системами.
"""

import logging

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError, KeycloakGetError, KeycloakPostError

from keycloak_userator.exceptions import (
    ConnectionError,
    AuthenticationError,
    AuthorizationError,
    GroupOperationError,
    UserCreationError,
)
from keycloak_userator.protocols import KeycloakProvider


class ConcreteKeycloakProvider(KeycloakProvider):
    """
    Конкретная реализация провайдера для работы с Keycloak Admin API.

    Инкапсулирует работу с python-keycloak клиентом, предоставляя
    чистый интерфейс без зависимости от реализации библиотеки.
    """

    def __init__(
        self,
        server_url: str,
        username: str,
        password: str,
        realm_name: str,
        verify: bool = True,
        dry_run: bool = False
    ):
        """
        Инициализация провайдера.

        Args:
            server_url: URL сервера Keycloak
            username: Логин администратора
            password: Пароль администратора
            realm_name: Имя realm
            verify: Проверка SSL сертификата
            dry_run: Режим сухой проверки (без реальных изменений)
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.realm_name = realm_name
        self.verify = verify
        self.dry_run = dry_run
        self._admin: KeycloakAdmin | None = None
        self._logger = logging.getLogger(__name__)

    @property
    def admin(self) -> KeycloakAdmin:
        """Получить клиент KeycloakAdmin."""
        if self._admin is None:
            raise ConnectionError(
                "Not connected",
                "Call connect() first"
            )
        return self._admin

    def connect(self) -> bool:
        """
        Подключение к серверу Keycloak.

        Returns:
            True если подключение успешно, иначе False
        """
        try:
            self._logger.info(f"Подключение к Keycloak: {self.server_url}")
            self._logger.info(f"Realm: {self.realm_name}")

            if self.dry_run:
                self._logger.warning("РЕЖИМ DRY-RUN: реальные операции не выполняются")
                return True

            self._admin = KeycloakAdmin(
                server_url=f"{self.server_url}/",
                username=self.username,
                password=self.password,
                realm_name=self.realm_name,
                verify=self.verify
            )

            # Проверка подключения через получение информации о realm
            realm_info = self._admin.get_realm(self.realm_name)
            self._logger.info(f"Успешное подключение к realm: {realm_info.get('realm', 'unknown')}")
            return True

        except KeycloakGetError as e:
            if e.response_code == 401:
                raise AuthenticationError(
                    "Неверные учётные данные",
                    f"Логин: {self.username}"
                ) from e
            elif e.response_code == 403:
                raise AuthorizationError(
                    "Недостаточно прав",
                    "Требуется роль realm-admin"
                ) from e
            else:
                raise ConnectionError(
                    "Ошибка подключения к Keycloak",
                    str(e)
                ) from e

        except KeycloakError as e:
            raise ConnectionError(
                "Ошибка подключения к Keycloak",
                str(e)
            ) from e

        except Exception as e:
            raise ConnectionError(
                "Неизвестная ошибка подключения",
                str(e)
            ) from e

    def get_or_create_group(self, group_name: str) -> str | None:
        """
        Получить или создать группу по имени.

        Args:
            group_name: Имя группы

        Returns:
            ID группы или None если ошибка

        Raises:
            GroupOperationError: При ошибке операции с группой
        """
        try:
            if self.dry_run:
                self._logger.info(f"[DRY-RUN] Группа '{group_name}' будет создана/найдена")
                return "dry-run-group-id"

            # Поиск существующей группы
            existing_groups = self.admin.get_groups(query={"search": group_name})

            for group in existing_groups:
                if group.get('name') == group_name:
                    group_id = group.get('id')
                    self._logger.info(f"Группа '{group_name}' уже существует (ID: {group_id})")
                    return group_id  # type: ignore[no-any-return]

            # Создание новой группы
            self._logger.info(f"Создание группы '{group_name}'")
            group_id = self.admin.create_group({'name': group_name})
            self._logger.info(f"Группа создана (ID: {group_id})")
            return group_id

        except KeycloakError as e:
            raise GroupOperationError(
                group_name,
                "Ошибка при работе с группой",
                str(e)
            ) from e

        except Exception as e:
            raise GroupOperationError(
                group_name,
                "Неизвестная ошибка при работе с группой",
                str(e)
            ) from e

    def user_exists(self, username: str) -> bool:
        """
        Проверить существование пользователя.

        Args:
            username: Имя пользователя

        Returns:
            True если пользователь существует, иначе False
        """
        try:
            if self.dry_run:
                return False

            users = self.admin.get_users(query={"search": username})
            return any(user.get('username') == username for user in users)

        except KeycloakError:
            # В случае ошибки считаем что пользователь не существует
            return False

        except Exception:
            # В случае неизвестной ошибки считаем что пользователь не существует
            return False

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

        Raises:
            UserCreationError: При ошибке создания пользователя
        """
        try:
            # Проверка существования пользователя
            if self.user_exists(username):
                self._logger.warning(f"Пользователь '{username}' уже существует - пропускаем")
                return None

            # Подготовка данных пользователя
            new_user = {
                'username': username,
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'enabled': True,
                'emailVerified': False,
                'credentials': [
                    {
                        'type': 'password',
                        'value': password,
                        'temporary': False
                    }
                ]
            }

            if self.dry_run:
                self._logger.info(f"[DRY-RUN] Пользователь '{username}' будет создан")
                return "dry-run-user-id"

            # Создание пользователя
            user_id = self.admin.create_user(new_user)
            self._logger.debug(f"Пользователь '{username}' создан (ID: {user_id})")

            # Добавление в группу (если указан group_id)
            if group_id:
                self.admin.group_user_add(user_id=user_id, group_id=group_id)
                self._logger.debug(f"Пользователь '{username}' добавлен в группу {group_id}")

            return user_id

        except KeycloakPostError as e:
            raise UserCreationError(
                username,
                "Ошибка Keycloak при создании пользователя",
                str(e)
            ) from e

        except KeycloakError as e:
            raise UserCreationError(
                username,
                "Ошибка при создании пользователя",
                str(e)
            ) from e

        except Exception as e:
            raise UserCreationError(
                username,
                "Неизвестная ошибка при создании пользователя",
                str(e)
            ) from e
