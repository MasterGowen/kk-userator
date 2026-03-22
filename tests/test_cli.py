#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cli.py

Тесты для CLI функций и основного потока приложения.

Покрывает:
- create_argument_parser
- get_credentials_from_input (с моком)
- get_credentials_from_env
- export_credentials
- main (с моками)
"""

import os
import argparse
from unittest.mock import Mock, patch

import pytest

from keycloak_userator.cli import (
    create_argument_parser,
    get_credentials_from_input,
    get_credentials_from_env,
    export_credentials,
    print_header,
    print_completion,
    main,
)
from keycloak_userator.config import Config, UserConfig, PasswordConfig, DefaultsConfig, LoggingConfig


@pytest.fixture
def default_config():
    """Конфигурация по умолчанию."""
    return Config(
        user=UserConfig(),
        password=PasswordConfig(),
        defaults=DefaultsConfig(),
        logging=LoggingConfig()
    )


# =============================================================================
# ТЕСТЫ ПАРСЕРА АРГУМЕНТОВ
# =============================================================================

class TestArgumentParser:
    """Тесты парсера аргументов."""

    def test_create_parser(self):
        """Создание парсера."""
        parser = create_argument_parser()

        assert isinstance(parser, argparse.ArgumentParser)

    def test_parse_count_argument(self):
        """Парсинг аргумента --count."""
        parser = create_argument_parser()
        args = parser.parse_args(['--count', '50'])

        assert args.count == 50

    def test_parse_count_short_argument(self):
        """Парсинг аргумента -n."""
        parser = create_argument_parser()
        args = parser.parse_args(['-n', '100'])

        assert args.count == 100

    def test_parse_start_argument(self):
        """Парсинг аргумента --start."""
        parser = create_argument_parser()
        args = parser.parse_args(['--start', '10'])

        assert args.start == 10

    def test_parse_start_short_argument(self):
        """Парсинг аргумента -s."""
        parser = create_argument_parser()
        args = parser.parse_args(['-s', '50'])

        assert args.start == 50

    def test_parse_dry_run_argument(self):
        """Парсинг аргумента --dry-run."""
        parser = create_argument_parser()
        args = parser.parse_args(['--dry-run'])

        assert args.dry_run is True

    def test_parse_output_dir_argument(self):
        """Парсинг аргумента --output-dir."""
        parser = create_argument_parser()
        args = parser.parse_args(['--output-dir', 'my_output'])

        assert args.output_dir == 'my_output'

    def test_parse_output_dir_short_argument(self):
        """Парсинг аргумента -o."""
        parser = create_argument_parser()
        args = parser.parse_args(['-o', 'custom_output'])

        assert args.output_dir == 'custom_output'

    def test_parse_no_interactive_argument(self):
        """Парсинг аргумента --no-interactive."""
        parser = create_argument_parser()
        args = parser.parse_args(['--no-interactive'])

        assert args.no_interactive is True

    def test_parse_config_argument(self):
        """Парсинг аргумента --config."""
        parser = create_argument_parser()
        args = parser.parse_args(['--config', 'custom.yaml'])

        assert args.config == 'custom.yaml'

    def test_parse_default_values(self):
        """Значения по умолчанию."""
        parser = create_argument_parser()
        args = parser.parse_args([])

        assert args.count is None
        assert args.start is None
        assert args.dry_run is False
        assert args.output_dir is None
        assert args.no_interactive is False
        assert args.config is None


# =============================================================================
# ТЕСТЫ GET_CREDENTIALS_FROM_INPUT
# =============================================================================

class TestGetCredentialsFromInput:
    """Тесты получения учётных данных из input."""

    @patch('keycloak_userator.cli.input')
    @patch('keycloak_userator.cli.print')
    def test_get_credentials_input(self, mock_print, mock_input, default_config):
        """Получение данных из input."""
        mock_input.side_effect = [
            'https://keycloak.example.com',  # URL
            'admin',                          # Username
            'password123',                    # Password
            'master'                          # Realm
        ]

        credentials = get_credentials_from_input(default_config)

        assert credentials['server_url'] == 'https://keycloak.example.com'
        assert credentials['username'] == 'admin'
        assert credentials['password'] == 'password123'
        assert credentials['realm'] == 'master'

    @patch('keycloak_userator.cli.input')
    def test_get_credentials_default_url(self, mock_input, default_config):
        """URL по умолчанию."""
        mock_input.side_effect = [
            '',  # URL (пустой → дефолт)
            'admin',
            'password123',
            'master'
        ]

        credentials = get_credentials_from_input(default_config)

        assert credentials['server_url'] == 'https://keycloak.urfu.online'

    @patch('keycloak_userator.cli.input')
    def test_get_credentials_empty_username(self, mock_input, default_config):
        """Пустой username вызывает exit."""
        mock_input.side_effect = [
            'https://keycloak.example.com',
            '',  # Пустой username
        ]

        with pytest.raises(SystemExit):
            get_credentials_from_input(default_config)

    @patch('keycloak_userator.cli.input')
    def test_get_credentials_empty_password(self, mock_input, default_config):
        """Пустой пароль вызывает exit."""
        mock_input.side_effect = [
            'https://keycloak.example.com',
            'admin',
            ''  # Пустой пароль
        ]

        with pytest.raises(SystemExit):
            get_credentials_from_input(default_config)

    @patch('keycloak_userator.cli.input')
    def test_get_credentials_default_realm(self, mock_input, default_config):
        """Realm по умолчанию."""
        mock_input.side_effect = [
            'https://keycloak.example.com',
            'admin',
            'password123',
            ''  # Пустой realm → дефолт
        ]

        credentials = get_credentials_from_input(default_config)

        assert credentials['realm'] == 'master'


# =============================================================================
# ТЕСТЫ GET_CREDENTIALS_FROM_ENV
# =============================================================================

class TestGetCredentialsFromEnv:
    """Тесты получения учётных данных из env."""

    def test_get_credentials_env_success(self, default_config):
        """Успешное получение из env."""
        os.environ['KEYCLOAK_URL'] = 'https://keycloak.example.com'
        os.environ['KEYCLOAK_USERNAME'] = 'admin'
        os.environ['KEYCLOAK_PASSWORD'] = 'password123'
        os.environ['KEYCLOAK_REALM'] = 'custom-realm'

        try:
            credentials = get_credentials_from_env(default_config)

            assert credentials['server_url'] == 'https://keycloak.example.com'
            assert credentials['username'] == 'admin'
            assert credentials['password'] == 'password123'
            assert credentials['realm'] == 'custom-realm'
        finally:
            os.environ.pop('KEYCLOAK_URL', None)
            os.environ.pop('KEYCLOAK_USERNAME', None)
            os.environ.pop('KEYCLOAK_PASSWORD', None)
            os.environ.pop('KEYCLOAK_REALM', None)

    def test_get_credentials_env_default_realm(self, default_config):
        """Realm по умолчанию из env."""
        os.environ['KEYCLOAK_URL'] = 'https://keycloak.example.com'
        os.environ['KEYCLOAK_USERNAME'] = 'admin'
        os.environ['KEYCLOAK_PASSWORD'] = 'password123'
        # KEYCLOAK_REALM не установлен

        try:
            credentials = get_credentials_from_env(default_config)

            assert credentials['realm'] == 'master'
        finally:
            os.environ.pop('KEYCLOAK_URL', None)
            os.environ.pop('KEYCLOAK_USERNAME', None)
            os.environ.pop('KEYCLOAK_PASSWORD', None)

    def test_get_credentials_env_missing(self, default_config):
        """Отсутствующие переменные env."""
        # Очищаем переменные окружения
        os.environ.pop('KEYCLOAK_URL', None)
        os.environ.pop('KEYCLOAK_USERNAME', None)
        os.environ.pop('KEYCLOAK_PASSWORD', None)

        credentials = get_credentials_from_env(default_config)

        assert credentials is None

    def test_get_credentials_env_missing_url(self, default_config):
        """Отсутствует KEYCLOAK_URL."""
        os.environ['KEYCLOAK_USERNAME'] = 'admin'
        os.environ['KEYCLOAK_PASSWORD'] = 'password123'
        os.environ.pop('KEYCLOAK_URL', None)

        try:
            credentials = get_credentials_from_env(default_config)
            assert credentials is None
        finally:
            os.environ.pop('KEYCLOAK_USERNAME', None)
            os.environ.pop('KEYCLOAK_PASSWORD', None)


# =============================================================================
# ТЕСТЫ EXPORT_CREDENTIALS
# =============================================================================

class TestExportCredentials:
    """Тесты экспорта учётных данных."""

    @patch('keycloak_userator.cli.CredentialExporter')
    @patch('keycloak_userator.cli.print')
    def test_export_credentials(self, mock_print, mock_exporter_class, tmp_path):
        """Экспорт учётных данных."""
        mock_exporter = Mock()
        mock_exporter.export_csv = Mock(return_value='/path/to/credentials.csv')
        mock_exporter.export_txt = Mock(return_value='/path/to/credentials.txt')
        mock_exporter.export_json = Mock(return_value='/path/to/credentials.json')
        mock_exporter_class.return_value = mock_exporter

        users = [
            {'username': 'user1', 'password': 'pass1'}
        ]

        export_credentials(users, str(tmp_path))

        mock_exporter_class.assert_called_once_with(output_dir=str(tmp_path))
        mock_exporter.export_csv.assert_called_once()
        mock_exporter.export_txt.assert_called_once()
        mock_exporter.export_json.assert_called_once()

    @patch('keycloak_userator.cli.os.path.abspath')
    @patch('keycloak_userator.cli.CredentialExporter')
    @patch('keycloak_userator.cli.print')
    def test_export_credentials_message(self, mock_print, mock_exporter_class, mock_abspath):
        """Сообщения при экспорте."""
        mock_exporter = Mock()
        mock_exporter.export_csv = Mock(return_value='/path/to/credentials.csv')
        mock_exporter.export_txt = Mock(return_value='/path/to/credentials.txt')
        mock_exporter.export_json = Mock(return_value='/path/to/credentials.json')
        mock_exporter_class.return_value = mock_exporter
        mock_abspath.return_value = '/absolute/path'

        users = [
            {'username': 'user1', 'password': 'pass1'}
        ]

        export_credentials(users, 'output')

        # Проверяем, что были вызовы print с предупреждением
        calls = [str(call) for call in mock_print.call_args_list]
        assert any('ВНИМАНИЕ' in call for call in calls)


# =============================================================================
# ТЕСТЫ PRINT_HEADER И PRINT_COMPLETION
# =============================================================================

class TestPrintFunctions:
    """Тесты функций вывода."""

    @patch('keycloak_userator.cli.print')
    def test_print_header(self, mock_print):
        """Вывод заголовка."""
        print_header()

        assert mock_print.called
        calls = [str(call) for call in mock_print.call_args_list]
        assert any('ГЕНЕРАТОР ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK' in call for call in calls)

    @patch('keycloak_userator.cli.print')
    def test_print_completion_success(self, mock_print):
        """Вывод завершения без ошибок."""
        stats = {'errors': 0, 'created': 10, 'skipped': 0, 'total': 10}

        print_completion(stats)

        assert mock_print.called

    @patch('keycloak_userator.cli.print')
    def test_print_completion_with_errors(self, mock_print):
        """Вывод завершения с ошибками."""
        stats = {'errors': 2, 'created': 8, 'skipped': 0, 'total': 10}

        print_completion(stats)

        calls = [str(call) for call in mock_print.call_args_list]
        assert any('Обнаружено ошибок: 2' in call for call in calls)


# =============================================================================
# ТЕСТЫ MAIN
# =============================================================================

class TestMain:
    """Тесты основной функции main."""

    @patch('keycloak_userator.cli.sys.exit')
    @patch('keycloak_userator.cli.print')
    @patch('keycloak_userator.cli.KeycloakUserGenerator')
    @patch('keycloak_userator.cli.load_application_config')
    @patch('keycloak_userator.cli.get_credentials_from_env')
    @patch('keycloak_userator.cli.get_credentials_from_input')
    @patch('keycloak_userator.cli.create_argument_parser')
    def test_main_dry_run(
        self,
        mock_create_parser,
        mock_get_input,
        mock_get_env,
        mock_load_config,
        mock_generator_class,
        mock_print,
        mock_exit,
        tmp_path
    ):
        """Запуск в режиме dry-run."""
        mock_args = Mock()
        mock_args.count = None
        mock_args.start = None
        mock_args.dry_run = True
        mock_args.output_dir = None
        mock_args.no_interactive = False
        mock_args.config = None
        mock_create_parser.return_value.parse_args = Mock(return_value=mock_args)

        mock_config = Mock()
        mock_config.config_path = 'config.yaml'
        mock_config.user.login_prefix = 'test'
        mock_config.user.email_domain = 'test.com'
        mock_config.user.group_name = 'test-group'
        mock_config.defaults.count = 5
        mock_config.defaults.start_number = 1
        mock_config.defaults.output_dir = str(tmp_path)
        mock_load_config.return_value = mock_config

        mock_credentials = {
            'server_url': 'https://keycloak.test.com',
            'username': 'admin',
            'password': 'password',
            'realm': 'master'
        }
        mock_get_input.return_value = mock_credentials

        mock_generator = Mock()
        mock_generator.connect = Mock(return_value=True)
        mock_generator.generate_users = Mock(return_value=[
            {'username': 'test_1', 'password': 'pass1'}
        ])
        mock_generator.stats = {'created': 5, 'skipped': 0, 'errors': 0, 'total': 5}
        mock_generator_class.return_value = mock_generator

        main()

        mock_generator.connect.assert_called_once()
        mock_generator.generate_users.assert_called_once()

    @patch('keycloak_userator.cli.sys.exit')
    @patch('keycloak_userator.cli.print')
    @patch('keycloak_userator.cli.export_credentials')
    @patch('keycloak_userator.cli.KeycloakUserGenerator')
    @patch('keycloak_userator.cli.load_application_config')
    @patch('keycloak_userator.cli.get_credentials_from_env')
    @patch('keycloak_userator.cli.get_credentials_from_input')
    @patch('keycloak_userator.cli.create_argument_parser')
    def test_main_connect_failure(
        self,
        mock_create_parser,
        mock_get_input,
        mock_get_env,
        mock_load_config,
        mock_generator_class,
        mock_export_credentials,
        mock_print,
        mock_exit,
        tmp_path
    ):
        """Ошибка подключения."""
        mock_args = Mock()
        mock_args.dry_run = False
        mock_create_parser.return_value.parse_args = Mock(return_value=mock_args)

        mock_config = Mock()
        mock_config.defaults.output_dir = str(tmp_path)
        mock_load_config.return_value = mock_config

        mock_credentials = {
            'server_url': 'https://keycloak.test.com',
            'username': 'admin',
            'password': 'password'
        }
        mock_get_input.return_value = mock_credentials

        mock_generator = Mock()
        mock_generator.connect = Mock(return_value=False)
        mock_generator.stats = {'created': 0, 'skipped': 0, 'errors': 0, 'total': 0}
        mock_generator_class.return_value = mock_generator

        result = main()

        # При ошибке подключения должен возвращаться 1
        assert result == 1
        # export_credentials не должен вызываться
        mock_export_credentials.assert_not_called()
