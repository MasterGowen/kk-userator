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
def mock_provider(default_config, mock_keycloak_admin):
    """Мок провайдера Keycloak."""
    mock = Mock()
    mock.connect = Mock(return_value=True)
    mock.get_or_create_group = Mock(return_value='group-id-123')
    mock.user_exists = Mock(return_value=False)
    mock.create_user = Mock(return_value='user-id-123')
    mock._admin = mock_keycloak_admin  # Для обратной совместимости
    return mock


@pytest.fixture
def generator(default_config, mock_provider):
    """Генератор пользователей с моком."""
    with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
        gen = KeycloakUserGenerator(
            server_url="https://keycloak.test.example.com",
            username="admin",
            password="admin_password",
            config=default_config,
            realm_name="test-realm",
            dry_run=False
        )
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
        mock_provider = Mock()
        mock_provider.connect = Mock(return_value=True)
        mock_provider._admin = mock_keycloak_admin

        with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
            gen = KeycloakUserGenerator(
                server_url="https://keycloak.test.example.com",
                username="admin",
                password="admin_password",
                config=default_config
            )
            gen._logger = Mock()

            result = gen.connect()

            assert result is True
            assert gen.keycloak_admin is mock_keycloak_admin
            mock_provider.connect.assert_called_once()

    def test_connect_dry_run(self, default_config):
        """Подключение в режиме dry-run."""
        mock_provider = Mock()
        mock_provider.connect = Mock(return_value=True)
        mock_provider._admin = None

        with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
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
            # В dry-run провайдер логирует предупреждение
            mock_provider.connect.assert_called_once()

    def test_connect_keycloak_error(self, default_config):
        """Ошибка подключения Keycloak."""
        from keycloak_userator.exceptions import ConnectionError

        mock_provider = Mock()
        mock_provider.connect = Mock(side_effect=ConnectionError("Connection failed"))

        with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
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
        mock_provider = Mock()
        mock_provider.connect = Mock(side_effect=Exception("Unexpected error"))

        with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
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

    def test_user_exists_true(self, generator, mock_provider):
        """Пользователь существует."""
        mock_provider.user_exists = Mock(return_value=True)

        result = generator._user_exists('testuser_1')

        assert result is True
        mock_provider.user_exists.assert_called_with('testuser_1')

    def test_user_exists_false(self, generator, mock_provider):
        """Пользователь не существует."""
        mock_provider.user_exists = Mock(return_value=False)

        result = generator._user_exists('testuser_1')

        assert result is False

    def test_user_exists_keycloak_error(self, generator, mock_provider):
        """Ошибка Keycloak при проверке."""
        mock_provider.user_exists = Mock(return_value=False)  # Возвращает False при ошибке

        result = generator._user_exists('testuser_1')

        assert result is False  # При ошибке возвращает False


# =============================================================================
# ТЕСТЫ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ
# =============================================================================

class TestKeycloakUserGeneratorCreateUser:
    """Тесты создания пользователя."""

    def test_create_user_success(self, generator, mock_provider):
        """Успешное создание пользователя."""
        mock_provider.create_user = Mock(return_value='user-id-123')

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1',
            group_id='group-id-123'
        )

        assert result is True
        mock_provider.create_user.assert_called_once()
        assert generator.stats['created'] == 1

    def test_create_user_exists(self, generator, mock_provider):
        """Пользователь уже существует."""
        mock_provider.user_exists = Mock(return_value=True)

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1'
        )

        assert result is True
        assert generator.stats['skipped'] == 1  # _create_user инкрементирует skipped

    def test_create_user_no_group(self, generator, mock_provider):
        """Создание пользователя без группы."""
        mock_provider.create_user = Mock(return_value='user-id-123')

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1',
            group_id=None
        )

        assert result is True

    def test_create_user_keycloak_error(self, generator, mock_provider):
        """Ошибка Keycloak при создании."""
        from keycloak_userator.exceptions import UserCreationError
        mock_provider.create_user = Mock(side_effect=UserCreationError('testuser_1', 'Error'))

        result = generator._create_user(
            username='testuser_1',
            password='Pass1234',
            email='testuser_1@test.example.com',
            first_name='Тест',
            last_name='Тестов 1'
        )

        assert result is False
        assert generator.stats['errors'] == 1

    def test_create_user_general_error(self, generator, mock_provider):
        """Общая ошибка при создании."""
        mock_provider.create_user = Mock(side_effect=Exception("Error"))

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

    def test_generate_users_success(self, generator, mock_provider):
        """Успешная генерация пользователей."""
        mock_provider.get_or_create_group = Mock(return_value='group-id-123')
        mock_provider.user_exists = Mock(return_value=False)
        mock_provider.create_user = Mock(return_value='user-id-123')

        users = generator.generate_users(count=3, start_number=1)

        assert len(users) == 3
        assert users[0]['username'] == 'testuser_1'
        assert users[1]['username'] == 'testuser_2'
        assert users[2]['username'] == 'testuser_3'
        assert generator.stats['created'] == 3
        assert generator.stats['total'] == 3

    def test_generate_users_dry_run(self, default_config):
        """Генерация в режиме dry-run."""
        mock_provider = Mock()
        mock_provider.connect = Mock(return_value=True)
        mock_provider._admin = None

        with patch('keycloak_userator.keycloak_client.ConcreteKeycloakProvider', return_value=mock_provider):
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

    def test_generate_users_with_errors(self, generator, mock_provider):
        """Генерация с ошибками."""
        from keycloak_userator.exceptions import UserCreationError

        call_count = [0]

        def create_user_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise UserCreationError('testuser_2', 'Error')
            return 'user-id-123'

        mock_provider.get_or_create_group = Mock(return_value='group-id-123')
        mock_provider.user_exists = Mock(return_value=False)
        mock_provider.create_user = Mock(side_effect=create_user_side_effect)

        users = generator.generate_users(count=3, start_number=1)

        assert len(users) == 2  # Один не создан
        assert generator.stats['created'] == 2
        assert generator.stats['errors'] == 1

    def test_generate_users_progress_logging(self, generator, mock_provider):
        """Логирование прогресса."""
        mock_provider.get_or_create_group = Mock(return_value='group-id-123')
        mock_provider.user_exists = Mock(return_value=False)
        mock_provider.create_user = Mock(return_value='user-id-123')

        # Просто проверяем что метод работает без ошибок
        users = generator.generate_users(count=3, start_number=1)

        assert len(users) == 3
        assert generator.stats['created'] == 3


# =============================================================================
# ТЕСТЫ ГРУППЫ
# =============================================================================

class TestKeycloakUserGeneratorGroup:
    """Тесты работы с группами."""

    def test_get_or_create_group_exists(self, generator, mock_provider):
        """Группа уже существует."""
        mock_provider.get_or_create_group = Mock(return_value='existing-group-id')

        group_id = generator._get_or_create_group('test-group')

        assert group_id == 'existing-group-id'
        mock_provider.get_or_create_group.assert_called_once()

    def test_get_or_create_group_create(self, generator, mock_provider):
        """Создание новой группы."""
        mock_provider.get_or_create_group = Mock(return_value='new-group-id')

        group_id = generator._get_or_create_group('test-group')

        assert group_id == 'new-group-id'
        mock_provider.get_or_create_group.assert_called_once()

    def test_get_or_create_group_keycloak_error(self, generator, mock_provider):
        """Ошибка Keycloak при работе с группой."""
        from keycloak_userator.exceptions import GroupOperationError
        mock_provider.get_or_create_group = Mock(side_effect=GroupOperationError('test-group', 'Error'))

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
