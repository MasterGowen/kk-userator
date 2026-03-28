#!/usr/bin/env python3
"""
cli.py

Точка входа приложения для генерации пользователей Keycloak.

Функциональность:
- Парсинг аргументов командной строки
- Получение учётных данных (input/env)
- Запуск генератора пользователей
"""

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from keycloak_userator.config import Config, ConfigValidationError, load_config
from keycloak_userator.exporter import CredentialExporter
from keycloak_userator.keycloak_client import KeycloakUserGenerator


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Создание парсера аргументов командной строки.

    Returns:
        Настроенный парсер аргументов
    """
    parser = argparse.ArgumentParser(
        description=(
            'Генератор пользователей Keycloak для курса '
            '"Английский для лиц с нарушениями зрения"'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m keycloak_userator.cli                    # Переменные окружения (по умолчанию)
  python -m keycloak_userator.cli --interactive      # Интерактивный режим
  python -m keycloak_userator.cli --count 50         # 50 пользователей
  python -m keycloak_userator.cli --dry-run          # Режим проверки

Переменные окружения (обязательно для неинтерактивного режима):
  KEYCLOAK_URL         URL сервера Keycloak
  KEYCLOAK_USERNAME    Имя пользователя администратора
  KEYCLOAK_PASSWORD    Пароль администратора
  KEYCLOAK_REALM       Имя realm (по умолчанию: master)
  KEYCLOAK_CONFIG      Путь к config.yaml
  KEYCLOAK_LOGIN_PREFIX  Префикс для логинов
  KEYCLOAK_EMAIL_DOMAIN  Домен для email
        """
    )

    parser.add_argument(
        '--count', '-n',
        type=int,
        default=None,
        help='Количество пользователей для создания'
    )

    parser.add_argument(
        '--start', '-s',
        type=int,
        default=None,
        help='Начальный номер для нумерации'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Режим сухой проверки (без реального создания)'
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Директория для файлов с учётными данными'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Интерактивный режим (запрос учётных данных)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Путь к файлу конфигурации (YAML)'
    )

    return parser


def get_credentials_from_input(config: Config) -> dict[str, str]:
    """
    Запрос учётных данных у пользователя через input().

    Args:
        config: Конфигурация приложения

    Returns:
        Словарь с данными для подключения
    """
    print("\n" + "=" * 60)
    print("ВВЕДИТЕ ДАННЫЕ ДЛЯ ПОДКЛЮЧЕНИЯ К KEYCLOAK")
    print("=" * 60 + "\n")

    server_url = input(
        "URL Keycloak (например, https://keycloak.urfu.online): "
    ).strip()
    if not server_url:
        server_url = "https://keycloak.urfu.online"

    username = input("Имя пользователя администратора: ").strip()
    if not username:
        print("Ошибка: имя пользователя не может быть пустым")
        sys.exit(1)

    password = input("Пароль администратора: ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым")
        sys.exit(1)

    realm = input(f"Realm [{config.user.default_realm}]: ").strip()
    if not realm:
        realm = config.user.default_realm

    return {
        'server_url': server_url,
        'username': username,
        'password': password,
        'realm': realm
    }


def get_credentials_from_env(config: Config) -> dict[str, str] | None:
    """
    Получение учётных данных из переменных окружения.

    Args:
        config: Конфигурация приложения

    Returns:
        Словарь с данными для подключения или None если переменные не найдены
    """
    server_url = os.environ.get('KEYCLOAK_URL')
    username = os.environ.get('KEYCLOAK_USERNAME')
    password = os.environ.get('KEYCLOAK_PASSWORD')
    realm = os.environ.get('KEYCLOAK_REALM', config.user.default_realm)

    if server_url and username and password:
        return {
            'server_url': server_url,
            'username': username,
            'password': password,
            'realm': realm
        }

    return None


def load_application_config(args: argparse.Namespace) -> Config:
    """
    Загрузка конфигурации приложения.

    Args:
        args: Аргументы командной строки

    Returns:
        Объект конфигурации
    """
    try:
        config_path = args.config or os.environ.get('KEYCLOAK_CONFIG')
        config = load_config(config_path) if config_path else load_config()

        if args.count is not None:
            config.defaults.count = args.count
        if args.start is not None:
            config.defaults.start_number = args.start
        if args.output_dir is not None:
            config.defaults.output_dir = args.output_dir

        return config

    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации не найден: {config_path}")
        sys.exit(1)
    except ConfigValidationError as e:
        print(f"Ошибка валидации конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        sys.exit(1)


def print_header() -> None:
    """Вывод заголовка приложения."""
    print("\n" + "=" * 60)
    print("ГЕНЕРАТОР ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK")
    print("Курс: Английский для лиц с нарушениями зрения")
    print("=" * 60 + "\n")


def export_credentials(users: list[dict[str, Any]], output_dir: str) -> None:
    """
    Экспорт учётных данных в файлы.

    Args:
        users: Список пользователей
        output_dir: Директория для сохранения
    """
    print("\n" + "=" * 60)
    print("ЭКСПОРТ УЧЁТНЫХ ДАННЫХ")
    print("=" * 60 + "\n")

    exporter = CredentialExporter(output_dir=output_dir)

    csv_file = exporter.export_csv(users)
    print(f"CSV файл сохранён: {csv_file}")

    txt_file = exporter.export_txt(users)
    print(f"TXT файл сохранён: {txt_file}")

    json_file = exporter.export_json(users)
    print(f"JSON файл сохранён: {json_file}")

    print(f"\nВсе файлы сохранены в директории: {os.path.abspath(output_dir)}")
    print("\n⚠️  ВНИМАНИЕ: Файлы содержат пароли в открытом виде!")
    print("   Обеспечьте безопасное хранение и передачу файлов.")


def print_completion(stats: dict[str, int]) -> None:
    """
    Вывод сообщения о завершении работы.

    Args:
        stats: Статистика выполнения
    """
    print("\n" + "=" * 60)
    print("РАБОТА ЗАВЕРШЕНА")
    print("=" * 60 + "\n")

    if stats['errors'] > 0:
        print(f"⚠️  Обнаружено ошибок: {stats['errors']}")


def main() -> int:
    """
    Точка входа в приложение.

    Returns:
        Код выхода (0 — успех, 1 — ошибка)
    """
    # Загрузка .env файла (если существует)
    load_dotenv()

    parser = create_argument_parser()
    args = parser.parse_args()

    print_header()

    config = load_application_config(args)

    if config.config_path:
        print(f"Конфигурация загружена: {config.config_path}")
    print(
        f"Параметры: префикс={config.user.login_prefix}, "
        f"домен={config.user.email_domain}, "
        f"группа={config.user.group_name}"
    )

    credentials: dict[str, str]

    if args.interactive:
        credentials = get_credentials_from_input(config)
        print("Введены данные для подключения")
    else:
        env_credentials = get_credentials_from_env(config)
        if not env_credentials:
            print("Ошибка: переменные окружения не найдены")
            print("Установите KEYCLOAK_URL, KEYCLOAK_USERNAME, KEYCLOAK_PASSWORD")
            print("Или используйте --interactive для интерактивного ввода")
            return 1
        credentials = env_credentials
        print("Использованы переменные окружения для подключения")

    generator = KeycloakUserGenerator(
        server_url=credentials['server_url'],
        username=credentials['username'],
        password=credentials['password'],
        config=config,
        realm_name=credentials.get('realm'),
        dry_run=args.dry_run
    )

    if not generator.connect():
        print("\nНе удалось подключиться к Keycloak. "
              "Проверьте данные и повторите попытку.")
        return 1

    created_users = generator.generate_users(
        count=config.defaults.count,
        start_number=config.defaults.start_number
    )

    if not args.dry_run and created_users:
        export_credentials(created_users, config.defaults.output_dir)

    print_completion(generator.stats)

    return 1 if generator.stats['errors'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
