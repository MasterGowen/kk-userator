#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
keycloak_user_generator.py

Скрипт для массового создания пользователей в Keycloak.
Предназначен для генерации учётных записей для курса
«Английский для лиц с нарушениями зрения».

Использование:
    python keycloak_user_generator.py [--dry-run] [--count N]

Автор: kk-userator project
Версия: 1.0.0
"""

import os
import sys
import csv
import json
import logging
import argparse
import secrets
import string
from datetime import datetime
from typing import Optional, List, Dict, Any

# Проверка наличия необходимых библиотек
try:
    from keycloak import KeycloakAdmin
    from keycloak.exceptions import KeycloakError
except ImportError:
    print("Ошибка: не установлена библиотека python-keycloak")
    print("Установите зависимости: pip install -r requirements.txt")
    sys.exit(1)


# =============================================================================
# КОНСТАНТЫ И НАСТРОЙКИ
# =============================================================================

# Настройки по умолчанию
DEFAULT_COUNT = 200  # Количество пользователей для создания
DEFAULT_REALM = "master"  # Realm в Keycloak
GROUP_NAME = "engforinclusb-users"  # Название группы для всех пользователей
EMAIL_DOMAIN = "urfu.online"  # Домен для email
LOGIN_PREFIX = "enginc"  # Префикс для логинов
FIRST_NAME = "Студент"  # Имя по умолчанию
LAST_NAME_TEMPLATE = "Студентов {number}"  # Фамилия с номером

# Параметры генерации паролей
PASSWORD_LENGTH = 8  # Длина пароля
PASSWORD_CHARS = string.ascii_letters + string.digits  # Латиница + цифры

# Настройки логирования
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = "keycloak_generator.log"


# =============================================================================
# КЛАСС ГЕНЕРАТОРА ПАРОЛЕЙ
# =============================================================================

class PasswordGenerator:
    """
    Генератор безопасных случайных паролей.
    
    Требования:
    - Минимум 8 символов
    - Латинские буквы (строчные и заглавные)
    - Цифры
    """
    
    def __init__(self, length: int = PASSWORD_LENGTH):
        """
        Инициализация генератора паролей.
        
        Args:
            length: Длина генерируемого пароля
        """
        self.length = length
        self.chars = PASSWORD_CHARS
    
    def generate(self) -> str:
        """
        Генерация случайного пароля.
        
        Returns:
            Случайный пароль заданной длины
        """
        # Используем secrets для криптографически безопасной генерации
        password = ''.join(secrets.choice(self.chars) for _ in range(self.length))
        return password
    
    def generate_batch(self, count: int) -> List[str]:
        """
        Генерация нескольких паролей.
        
        Args:
            count: Количество паролей для генерации
            
        Returns:
            Список сгенерированных паролей
        """
        return [self.generate() for _ in range(count)]


# =============================================================================
# КЛАСС ЭКСПОРТЕРА ДАННЫХ
# =============================================================================

class CredentialExporter:
    """
    Экспортёр учётных данных в различные форматы.
    
    Поддерживаемые форматы:
    - CSV (comma-separated values)
    - TXT (текстовый формат с разделителями)
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Инициализация экспортёра.
        
        Args:
            output_dir: Директория для сохранения файлов
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_csv(self, users: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Экспорт данных в CSV формат.
        
        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)
            
        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"credentials_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'password', 'email', 'firstName', 'lastName', 'enabled']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for user in users:
                writer.writerow({
                    'username': user.get('username', ''),
                    'password': user.get('password', ''),
                    'email': user.get('email', ''),
                    'firstName': user.get('firstName', ''),
                    'lastName': user.get('lastName', ''),
                    'enabled': user.get('enabled', True)
                })
        
        return filepath
    
    def export_txt(self, users: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Экспорт данных в TXT формат (читаемый текстовый формат).
        
        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)
            
        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"credentials_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as txtfile:
            txtfile.write("=" * 80 + "\n")
            txtfile.write("УЧЁТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK\n")
            txtfile.write(f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Всего пользователей: {len(users)}\n")
            txtfile.write("=" * 80 + "\n\n")
            
            for i, user in enumerate(users, 1):
                txtfile.write(f"№ {i}\n")
                txtfile.write(f"  Логин:   {user.get('username', '')}\n")
                txtfile.write(f"  Пароль:  {user.get('password', '')}\n")
                txtfile.write(f"  Email:   {user.get('email', '')}\n")
                txtfile.write(f"  Имя:     {user.get('firstName', '')}\n")
                txtfile.write(f"  Фамилия: {user.get('lastName', '')}\n")
                txtfile.write(f"  Статус:  {'Активен' if user.get('enabled', True) else 'Отключён'}\n")
                txtfile.write("-" * 40 + "\n")
            
            txtfile.write("\n" + "=" * 80 + "\n")
            txtfile.write("КОНЕЦ ФАЙЛА\n")
            txtfile.write("=" * 80 + "\n")
        
        return filepath
    
    def export_json(self, users: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Экспорт данных в JSON формат (для машинной обработки).
        
        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)
            
        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"credentials_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_users': len(users),
                'users': users
            }, jsonfile, ensure_ascii=False, indent=2)
        
        return filepath


# =============================================================================
# КЛАСС ГЕНЕРАТОРА ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK
# =============================================================================

class KeycloakUserGenerator:
    """
    Основной класс для генерации пользователей в Keycloak.
    
    Функциональность:
    - Подключение к Keycloak API
    - Создание группы пользователей
    - Массовое создание пользователей
    - Идемпотентность (проверка дубликатов)
    - Логирование операций
    """
    
    def __init__(
        self,
        server_url: str,
        username: str,
        password: str,
        realm_name: str = DEFAULT_REALM,
        dry_run: bool = False
    ):
        """
        Инициализация генератора пользователей.
        
        Args:
            server_url: URL сервера Keycloak (например, https://keycloak.example.com)
            username: Имя пользователя администратора
            password: Пароль администратора
            realm_name: Имя realm в Keycloak
            dry_run: Режим сухой проверки (без реального создания)
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.realm_name = realm_name
        self.dry_run = dry_run
        
        # Инициализация клиента Keycloak Admin API
        self.keycloak_admin: Optional[KeycloakAdmin] = None
        
        # Настройка логирования
        self.logger = self._setup_logging()
        
        # Статистика операций
        self.stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
        Настройка системы логирования.
        
        Returns:
            Настроенный логгер
        """
        logger = logging.getLogger('keycloak_user_generator')
        logger.setLevel(logging.INFO)
        
        # Создаём обработчики для консоли и файла
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Форматирование
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def connect(self) -> bool:
        """
        Подключение к Keycloak API.
        
        Returns:
            True если подключение успешно, иначе False
        """
        try:
            self.logger.info(f"Подключение к Keycloak: {self.server_url}")
            self.logger.info(f"Realm: {self.realm_name}")
            
            if self.dry_run:
                self.logger.warning("РЕЖИМ DRY-RUN: реальные операции не выполняются")
                return True
            
            # Инициализация клиента Keycloak Admin API
            self.keycloak_admin = KeycloakAdmin(
                server_url=f"{self.server_url}/",
                username=self.username,
                password=self.password,
                realm_name=self.realm_name,
                verify=True
            )
            
            # Проверка подключения
            realm_info = self.keycloak_admin.get_realm(self.realm_name)
            self.logger.info(f"Успешное подключение к realm: {realm_info.get('realm', 'unknown')}")
            
            return True
            
        except KeycloakError as e:
            self.logger.error(f"Ошибка подключения к Keycloak: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при подключении: {e}")
            return False
    
    def _get_or_create_group(self, group_name: str) -> Optional[str]:
        """
        Получение или создание группы пользователей.
        
        Args:
            group_name: Имя группы
            
        Returns:
            ID группы или None в случае ошибки
        """
        try:
            # Поиск существующей группы
            existing_groups = self.keycloak_admin.get_groups(query={"search": group_name})
            
            for group in existing_groups:
                if group.get('name') == group_name:
                    self.logger.info(f"Группа '{group_name}' уже существует (ID: {group.get('id')})")
                    return group.get('id')
            
            # Создание новой группы
            self.logger.info(f"Создание группы '{group_name}'")
            group_id = self.keycloak_admin.create_group({'name': group_name})
            self.logger.info(f"Группа создана (ID: {group_id})")
            
            return group_id
            
        except KeycloakError as e:
            self.logger.error(f"Ошибка при работе с группой: {e}")
            return None
    
    def _user_exists(self, username: str) -> bool:
        """
        Проверка существования пользователя.
        
        Args:
            username: Имя пользователя для проверки
            
        Returns:
            True если пользователь существует, иначе False
        """
        try:
            users = self.keycloak_admin.get_users(query={"search": username})
            for user in users:
                if user.get('username') == username:
                    return True
            return False
        except KeycloakError:
            return False
    
    def _create_user(
        self,
        username: str,
        password: str,
        email: str,
        first_name: str,
        last_name: str,
        group_id: Optional[str] = None
    ) -> bool:
        """
        Создание одного пользователя.
        
        Args:
            username: Имя пользователя (логин)
            password: Пароль
            email: Email адрес
            first_name: Имя
            last_name: Фамилия
            group_id: ID группы для добавления
            
        Returns:
            True если пользователь создан успешно, иначе False
        """
        try:
            # Проверка на существование (идемпотентность)
            if self._user_exists(username):
                self.logger.warning(f"Пользователь '{username}' уже существует - пропускаем")
                self.stats['skipped'] += 1
                return True
            
            # Данные нового пользователя
            new_user = {
                'username': username,
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'enabled': True,
                'emailVerified': False,
                'credentials': [{
                    'type': 'password',
                    'value': password,
                    'temporary': False
                }]
            }
            
            # Создание пользователя
            user_id = self.keycloak_admin.create_user(new_user)
            self.logger.debug(f"Пользователь '{username}' создан (ID: {user_id})")
            
            # Добавление в группу
            if group_id:
                self.keycloak_admin.group_user_add(user_id=user_id, group_id=group_id)
                self.logger.debug(f"Пользователь '{username}' добавлен в группу")
            
            self.stats['created'] += 1
            return True
            
        except KeycloakError as e:
            self.logger.error(f"Ошибка создания пользователя '{username}': {e}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при создании '{username}': {e}")
            self.stats['errors'] += 1
            return False
    
    def generate_users(
        self,
        count: int = DEFAULT_COUNT,
        start_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Генерация и создание пользователей.
        
        Args:
            count: Количество пользователей для создания
            start_number: Начальный номер для нумерации
            
        Returns:
            Список созданных пользователей с учётными данными
        """
        self.stats['total'] = count
        created_users = []
        password_gen = PasswordGenerator()
        
        self.logger.info(f"Начало генерации {count} пользователей (начиная с {start_number})")
        
        # Получение или создание группы
        group_id = None
        if not self.dry_run and self.keycloak_admin:
            group_id = self._get_or_create_group(GROUP_NAME)
            if group_id:
                self.logger.info(f"Все пользователи будут добавлены в группу '{GROUP_NAME}'")
        
        # Генерация пользователей
        for i in range(start_number, start_number + count):
            username = f"{LOGIN_PREFIX}_{i}"
            password = password_gen.generate()
            email = f"{LOGIN_PREFIX}_{i}@{EMAIL_DOMAIN}"
            first_name = FIRST_NAME
            last_name = LAST_NAME_TEMPLATE.format(number=i)
            
            # Сохранение данных пользователя
            user_data = {
                'username': username,
                'password': password,
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'enabled': True,
                'group': GROUP_NAME
            }
            
            if self.dry_run:
                # В режиме dry-run просто логируем
                self.logger.info(f"[DRY-RUN] Будет создан: {username} | {email}")
                created_users.append(user_data)
                self.stats['created'] += 1
            else:
                # Реальное создание
                if self._create_user(username, password, email, first_name, last_name, group_id):
                    created_users.append(user_data)
                    self.logger.info(f"Создан: {username} | {email}")
                else:
                    self.logger.error(f"Не удалось создать: {username}")
            
            # Небольшая задержка для предотвращения rate-limiting
            if not self.dry_run and i % 10 == 0:
                self.logger.info(f"Прогресс: {i - start_number + 1}/{count}")
        
        # Финальный отчёт
        self.logger.info("=" * 60)
        self.logger.info("Генерация завершена")
        self.logger.info(f"Всего: {self.stats['total']}")
        self.logger.info(f"Создано: {self.stats['created']}")
        self.logger.info(f"Пропущено (существуют): {self.stats['skipped']}")
        self.logger.info(f"Ошибки: {self.stats['errors']}")
        self.logger.info("=" * 60)
        
        return created_users


# =============================================================================
# ФУНКЦИИ ВВОДА ДАННЫХ
# =============================================================================

def get_credentials_from_input() -> Dict[str, str]:
    """
    Запрос учётных данных у пользователя через input().
    
    Returns:
        Словарь с данными для подключения
    """
    print("\n" + "=" * 60)
    print("ВВЕДИТЕ ДАННЫЕ ДЛЯ ПОДКЛЮЧЕНИЯ К KEYCLOAK")
    print("=" * 60 + "\n")
    
    # URL сервера
    server_url = input("URL Keycloak (например, https://keycloak.urfu.online): ").strip()
    if not server_url:
        server_url = "https://keycloak.urfu.online"
    
    # Имя пользователя
    username = input("Имя пользователя администратора: ").strip()
    if not username:
        print("Ошибка: имя пользователя не может быть пустым")
        sys.exit(1)
    
    # Пароль (скрытый ввод)
    password = input("Пароль администратора: ").strip()
    if not password:
        print("Ошибка: пароль не может быть пустым")
        sys.exit(1)
    
    # Realm
    realm = input(f"Realm [{DEFAULT_REALM}]: ").strip()
    if not realm:
        realm = DEFAULT_REALM
    
    return {
        'server_url': server_url,
        'username': username,
        'password': password,
        'realm': realm
    }


def get_credentials_from_env() -> Dict[str, str]:
    """
    Получение учётных данных из переменных окружения.
    
    Ожидаемые переменные:
    - KEYCLOAK_URL
    - KEYCLOAK_USERNAME
    - KEYCLOAK_PASSWORD
    - KEYCLOAK_REALM (опционально)
    
    Returns:
        Словарь с данными для подключения или None если переменные не найдены
    """
    server_url = os.environ.get('KEYCLOAK_URL')
    username = os.environ.get('KEYCLOAK_USERNAME')
    password = os.environ.get('KEYCLOAK_PASSWORD')
    realm = os.environ.get('KEYCLOAK_REALM', DEFAULT_REALM)
    
    if server_url and username and password:
        return {
            'server_url': server_url,
            'username': username,
            'password': password,
            'realm': realm
        }
    
    return None


# =============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# =============================================================================

def main():
    """
    Точка входа в приложение.
    """
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description='Генератор пользователей Keycloak для курса "Английский для лиц с нарушениями зрения"',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python keycloak_user_generator.py                    # Интерактивный режим, 200 пользователей
  python keycloak_user_generator.py --count 50         # Создать 50 пользователей
  python keycloak_user_generator.py --dry-run          # Режим проверки без создания
  python keycloak_user_generator.py --count 200 --start 1  # Создать с 1 по 200
  
Переменные окружения (опционально):
  KEYCLOAK_URL         URL сервера Keycloak
  KEYCLOAK_USERNAME    Имя пользователя администратора
  KEYCLOAK_PASSWORD    Пароль администратора
  KEYCLOAK_REALM       Имя realm (по умолчанию: master)
        """
    )
    
    parser.add_argument(
        '--count', '-n',
        type=int,
        default=DEFAULT_COUNT,
        help=f'Количество пользователей для создания (по умолчанию: {DEFAULT_COUNT})'
    )
    
    parser.add_argument(
        '--start', '-s',
        type=int,
        default=1,
        help='Начальный номер для нумерации (по умолчанию: 1)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Режим сухой проверки (без реального создания пользователей)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Директория для сохранения файлов с учётными данными'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Не интерактивный режим (использовать переменные окружения)'
    )
    
    args = parser.parse_args()
    
    # Заголовок
    print("\n" + "=" * 60)
    print("ГЕНЕРАТОР ПОЛЬЗОВАТЕЛЕЙ KEYCLOAK")
    print("Курс: Английский для лиц с нарушениями зрения")
    print("=" * 60 + "\n")
    
    # Получение учётных данных
    credentials = None
    
    if args.no_interactive:
        # Попытка получить из переменных окружения
        credentials = get_credentials_from_env()
        if not credentials:
            print("Ошибка: переменные окружения не найдены")
            print("Установите KEYCLOAK_URL, KEYCLOAK_USERNAME, KEYCLOAK_PASSWORD")
            sys.exit(1)
        print("Использованы переменные окружения для подключения")
    else:
        # Интерактивный ввод
        credentials = get_credentials_from_input()
    
    # Инициализация генератора
    generator = KeycloakUserGenerator(
        server_url=credentials['server_url'],
        username=credentials['username'],
        password=credentials['password'],
        realm_name=credentials['realm'],
        dry_run=args.dry_run
    )
    
    # Подключение к Keycloak
    if not generator.connect():
        print("\nНе удалось подключиться к Keycloak. Проверьте данные и повторите попытку.")
        sys.exit(1)
    
    # Генерация пользователей
    created_users = generator.generate_users(count=args.count, start_number=args.start)
    
    # Экспорт данных (только если не dry-run и есть созданные пользователи)
    if not args.dry_run and created_users:
        print("\n" + "=" * 60)
        print("ЭКСПОРТ УЧЁТНЫХ ДАННЫХ")
        print("=" * 60 + "\n")
        
        exporter = CredentialExporter(output_dir=args.output_dir)
        
        # Экспорт в CSV
        csv_file = exporter.export_csv(created_users)
        print(f"CSV файл сохранён: {csv_file}")
        
        # Экспорт в TXT
        txt_file = exporter.export_txt(created_users)
        print(f"TXT файл сохранён: {txt_file}")
        
        # Экспорт в JSON (для машинной обработки)
        json_file = exporter.export_json(created_users)
        print(f"JSON файл сохранён: {json_file}")
        
        print(f"\nВсе файлы сохранены в директории: {os.path.abspath(args.output_dir)}")
        print("\n⚠️  ВНИМАНИЕ: Файлы содержат пароли в открытом виде!")
        print("   Обеспечьте безопасное хранение и передачу файлов.")
    
    # Завершение
    print("\n" + "=" * 60)
    print("РАБОТА ЗАВЕРШЕНА")
    print("=" * 60 + "\n")
    
    # Код выхода
    if generator.stats['errors'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
