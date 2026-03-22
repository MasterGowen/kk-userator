#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_keycloak_client.py

Тесты для генератора пользователей Keycloak KeycloakUserGenerator.

Покрывает:
- Подключение к Keycloak
- Проверку существования пользователя
- Создание пользователя
- Генерацию данных пользователя
- Массовую генерацию
- Режим dry-run
"""

from unittest.mock import Mock, patch

import pytest

from keycloak_userator.config import Config, UserConfig, PasswordConfig, DefaultsConfig, LoggingConfig
from keycloak_userator.keycloak_client import KeycloakUserGenerator


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def default_config():
    """Конфигурация по умолчанию."""
    return Config(
        user=UserConfig(
            login_prefix="testuser",
            email_domain="test.example.com",
            first_name="Тест",
            last_name_template="Тестов {number}",
            group_name="test-group"
        ),
        password=PasswordConfig(),
        defaults=DefaultsConfig(),
        logging=LoggingConfig()
    )


@pytest.fixture
def mock_keycloak_admin():
    """Мок KeycloakAdmin."""
    mock = Mock()
    mock.get_realm = Mock(return_value={'realm': 'test-realm'})
    mock.get_groups = Mock(return_value=[])
    mock.create_group = Mock(return_value='group-id-123')
    mock.get_users = Mock(return_value=[])
    mock.create_user = Mock(return_value='user-id-123')
    mock.group_user_add = Mock(return_value=None)
    return mock


@pytest.fixture
def generator(default_config, mock_keycloak_admin):
    """Генератор пользователей с моком."""
    gen = KeycloakUserGenerator(
        server_url="https://keycloak.test.example.com",
        username="admin",
        password="admin_password",
        config=default_config,
        realm_name="test-realm",
        dry_run=False
    )
    gen.keycloak_admin = mock_keycloak_admin
    gen._logger = Mock()
    return gen


# =============================================================================
# ТЕСТЫ ИНИЦИАЛИЗАЦИИ
# =============================================================================

class TestKeycloakUserGeneratorInit:
    """Тесты инициализации KeycloakUserGenerator."""

    def test_init(self, default_config):
        """Инициализация генератора."""
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config,
            realm_name="test-realm",
            dry_run=False
        )

        assert gen.server_url == "https://keycloak.test.example.com"
        assert gen.username == "admin"
        assert gen.password == "admin_password"
        assert gen.realm_name == "test-realm"
        assert gen.config == default_config
        assert gen.dry_run is False
        assert gen.keycloak_admin is None
        assert gen.stats == {'created': 0, 'skipped': 0, 'errors': 0, 'total': 0}

    def test_init_dry_run(self, default_config):
        """Инициализация в режиме dry-run."""
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config,
            dry_run=True
        )

        assert gen.dry_run is True

    def test_init_default_realm(self, default_config):
        """Инициализация с realm по умолчанию."""
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config
        )

        assert gen.realm_name == "master"  # Из Config


# =============================================================================
# ТЕСТЫ ПОДКЛЮЧЕНИЯ
# =============================================================================

class TestKeycloakUserGeneratorConnect:
    """Тесты подключения к Keycloak."""

    def test_connect_success(self, default_config, mock_keycloak_admin):
        """Успешное подключение."""
        with patch('keycloak_userator.keycloak_client.KeycloakAdmin', return_value=mock_keycloak_admin):
            gen = KeycloakUserGenerator(
                server_url="https://keycloak.test.example.com",
                username="admin",
                password="admin_password",
                config=default_config
            )
            gen._logger = Mock()

            result = gen.connect()

            assert result is True
            assert gen.keycloak_admin is not None
            gen._logger.info.assert_any_call("Успешное подключение к realm: test-realm")

    def test_connect_dry_run(self, default_config):
        """Подключение в режиме dry-run."""
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config,
            dry_run=True
        )
        gen._logger = Mock()

        result = gen.connect()

        assert result is True
        assert gen.keycloak_admin is None
        gen._logger.warning.assert_called_with(
            "РЕЖИМ DRY-RUN: реальные операции не выполняются"
        )

    def test_connect_keycloak_error(self, default_config):
        """Ошибка подключения Keycloak."""
        from keycloak.exceptions import KeycloakError

        with patch('keycloak_userator.keycloak_client.KeycloakAdmin') as mock_admin:
            mock_admin.side_effect = KeycloakError("Connection failed")

            gen = KeycloakUserGenerator(
                server_url="https://keycloak.test.example.com",
                username="admin",
                password="admin_password",
                config=default_config
            )
            gen._logger = Mock()

            result = gen.connect()

            assert result is False
            gen._logger.error.assert_called()

    def test_connect_general_error(self, default_config):
        """Общая ошибка подключения."""
        with patch('keycloak_userator.keycloak_client.KeycloakAdmin') as mock_admin:
            mock_admin.side_effect = Exception("Unexpected error")

            gen = KeycloakUserGenerator(
                server_url="https://keycloak.test.example.com",
                username="admin",
                password="admin_password",
                config=default_config
            )
            gen._logger = Mock()

            result = gen.connect()

            assert result is False
            gen._logger.error.assert_called()


# =============================================================================
# ТЕСТЫ ПРОВЕРКИ СУЩЕСТВОВАНИЯ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

class TestKeycloakUserGeneratorUserExists:
    """Тесты проверки существования пользователя."""

    def test_user_exists_true(self, generator, mock_keycloak_admin):
        """Пользователь существует."""
        mock_keycloak_admin.get_users = Mock(return_value=[
            {'username': 'testuser_1'}
        ])

        result = generator._user_exists('testuser_1')

        assert result is True
        mock_keycloak_admin.get_users.assert_called_with(query={"search": "testuser_1"})

    def test_user_exists_false(self, generator, mock_keycloak_admin):
        """Пользователь не существует."""
        mock_keycloak_admin.get_users = Mock(return_value=[])

        result = generator._user_exists('testuser_1')

        assert result is False

    def test_user_exists_keycloak_error(self, generator, mock_keycloak_admin):
        """Ошибка Keycloak при проверке."""
        from keycloak.exceptions import KeycloakError
        mock_keycloak_admin.get_users = Mock(side_effect=KeycloakError("Error"))

        result = generator._user_exists('testuser_1')

        assert result is False


# =============================================================================
# ТЕСТЫ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

class TestKeycloakUserGeneratorCreateUser:
    """Тесты создания пользователя."""

    def test_create_user_success(self, generator, mock_keycloak_admin):
        """Успешное создание пользователя."""
        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1',
            group_id='group-id-123'
        )

        assert result is True
        mock_keycloak_admin.create_user.assert_called_once()
        mock_keycloak_admin.group_user_add.assert_called_once()
        assert generator.stats['created'] == 1

    def test_create_user_exists(self, generator, mock_keycloak_admin):
        """Пользователь уже существует."""
        generator._user_exists = Mock(return_value=True)

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1'
        )

        assert result is True
        mock_keycloak_admin.create_user.assert_not_called()
        assert generator.stats['skipped'] == 1

    def test_create_user_no_group(self, generator, mock_keycloak_admin):
        """Создание пользователя без группы."""
        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1',
            group_id=None
        )

        assert result is True
        mock_keycloak_admin.group_user_add.assert_not_called()

    def test_create_user_keycloak_error(self, generator, mock_keycloak_admin):
        """Ошибка Keycloak при создании."""
        from keycloak.exceptions import KeycloakError
        mock_keycloak_admin.create_user = Mock(side_effect=KeycloakError("Error"))

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1'
        )

        assert result is False
        assert generator.stats['errors'] == 1

    def test_create_user_general_error(self, generator, mock_keycloak_admin):
        """Общая ошибка при создании."""
        mock_keycloak_admin.create_user = Mock(side_effect=Exception("Error"))

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1'
        )

        assert result is False
        assert generator.stats['errors'] == 1


# =============================================================================
# ТЕСТЫ ГЕНЕРАЦИИ ДАННЫХ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

class TestKeycloakUserGeneratorGenerateUserData:
    """Тесты генерации данных пользователя."""

    def test_generate_user_data(self, generator, default_config):
        """Генерация данных пользователя."""
        user_data = generator._generate_user_data(
            number=1,
            password='Pass1234'
        )

        assert user_data['username'] == 'testuser_1'
        assert user_data['email'] == 'testuser_1@test.example.com'
        assert user_data['firstName'] == 'Тест'
        assert user_data['lastName'] == 'Тестов 1'
        assert user_data['enabled'] is True
        assert user_data['password'] == 'Pass1234'
        assert user_data['group'] == 'test-group'

    def test_generate_user_data_different_number(self, generator, default_config):
        """Генерация данных для разных номеров."""
        user_data_1 = generator._generate_user_data(number=1, password='Pass1234')
        user_data_10 = generator._generate_user_data(number=10, password='Pass5678')

        assert user_data_1['username'] == 'testuser_1'
        assert user_data_10['username'] == 'testuser_10'
        assert user_data_1['email'] == 'testuser_1@test.example.com'
        assert user_data_10['email'] == 'testuser_10@test.example.com'
        assert user_data_1['lastName'] == 'Тестов 1'
        assert user_data_10['lastName'] == 'Тестов 10'


# =============================================================================
# ТЕСТЫ МАССОВОЙ ГЕНЕРАЦИИ
# =============================================================================

class TestKeycloakUserGeneratorGenerateUsers:
    """Тесты массовой генерации пользователей."""

    def test_generate_users_success(self, generator, mock_keycloak_admin):
        """Успешная генерация пользователей."""
        mock_keycloak_admin.get_groups = Mock(return_value=[{'id': 'group-id-123', 'name': 'test-group'}])

        users = generator.generate_users(count=3, start_number=1)

        assert len(users) == 3
        assert users[0]['username'] == 'testuser_1'
        assert users[1]['username'] == 'testuser_2'
        assert users[2]['username'] == 'testuser_3'
        assert generator.stats['created'] == 3
        assert generator.stats['total'] == 3

    def test_generate_users_dry_run(self, default_config):
        """Генерация в режиме dry-run."""
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config,
            dry_run=True
        )
        gen._logger = Mock()

        users = gen.generate_users(count=3, start_number=1)

        assert len(users) == 3
        assert gen.stats['created'] == 3
        # В dry-run не должно быть вызовов API
        assert gen.keycloak_admin is None

    def test_generate_users_with_errors(self, generator, mock_keycloak_admin):
        """Генерация с ошибками."""
        # Первый пользователь создаётся успешно, второй с ошибкой
        call_count = [0]

        def create_user_side_effect(user_data):
            call_count[0] += 1
            if call_count[0] == 2:
                from keycloak.exceptions import KeycloakError
                raise KeycloakError("Error")
            return 'user-id-123'

        mock_keycloak_admin.create_user = Mock(side_effect=create_user_side_effect)
        mock_keycloak_admin.get_groups = Mock(return_value=[{'id': 'group-id-123', 'name': 'test-group'}])

        users = generator.generate_users(count=3, start_number=1)

        assert len(users) == 2  # Один не создан
        assert generator.stats['created'] == 2
        assert generator.stats['errors'] == 1

    def test_generate_users_progress_logging(self, generator, mock_keycloak_admin):
        """Логирование прогресса."""
        mock_keycloak_admin.get_groups = Mock(return_value=[{'id': 'group-id-123', 'name': 'test-group'}])

        generator.generate_users(count=15, start_number=1)

        # Проверяем, что логирование прогресса вызывалось (каждые 10 пользователей)
        # Прогресс должен логироваться на 10-м пользователе
        info_calls = [str(call) for call in generator._logger.info.call_args_list]
        progress_logged = any('Прогресс' in call for call in info_calls)
        assert progress_logged is True


# =============================================================================
# ТЕСТЫ ГРУППЫ
# =============================================================================

class TestKeycloakUserGeneratorGroup:
    """Тесты работы с группами."""

    def test_get_or_create_group_exists(self, generator, mock_keycloak_admin):
        """Группа уже существует."""
        mock_keycloak_admin.get_groups = Mock(return_value=[
            {'id': 'existing-group-id', 'name': 'test-group'}
        ])

        group_id = generator._get_or_create_group('test-group')

        assert group_id == 'existing-group-id'
        mock_keycloak_admin.create_group.assert_not_called()

    def test_get_or_create_group_create(self, generator, mock_keycloak_admin):
        """Создание новой группы."""
        mock_keycloak_admin.get_groups = Mock(return_value=[])
        mock_keycloak_admin.create_group = Mock(return_value='new-group-id')

        group_id = generator._get_or_create_group('test-group')

        assert group_id == 'new-group-id'
        mock_keycloak_admin.create_group.assert_called_once()

    def test_get_or_create_group_keycloak_error(self, generator, mock_keycloak_admin):
        """Ошибка Keycloak при работе с группой."""
        from keycloak.exceptions import KeycloakError
        mock_keycloak_admin.get_groups = Mock(side_effect=KeycloakError("Error"))

        group_id = generator._get_or_create_group('test-group')

        assert group_id is None


# =============================================================================
# ТЕСТЫ ЛОГИРОВАНИЯ
# =============================================================================

class TestKeycloakUserGeneratorLogging:
    """Тесты логирования."""

    def test_log_final_report(self, generator):
        """Логирование финального отчёта."""
        generator.stats = {
            'total': 10,
            'created': 8,
            'skipped': 1,
            'errors': 1
        }

        generator._log_final_report()

        # Проверяем, что логгер был вызван
        assert generator._logger.info.called
        calls = [str(call) for call in generator._logger.info.call_args_list]

        assert any('Генерация завершена' in call for call in calls)
        assert any('Всего: 10' in call for call in calls)
        assert any('Создано: 8' in call for call in calls)
        assert any('Пропущено' in call for call in calls)
        assert any('Ошибки: 1' in call for call in calls)

    def test_logger_lazy_initialization(self, generator):
        """Ленивая инициализация логгера."""
        # Убираем логгер, если он был создан
        if hasattr(generator, '_logger'):
            delattr(generator, '_logger')

        # При первом обращении логгер должен создаться
        logger = generator.logger

        assert logger is not None
        assert hasattr(generator, '_logger')
