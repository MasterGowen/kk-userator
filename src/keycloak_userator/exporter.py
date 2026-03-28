#!/usr/bin/env python3
"""
exporter.py

Экспортёр учётных данных в различные форматы.

Поддерживаемые форматы:
- CSV (comma-separated values)
- TXT (текстовый формат с разделителями)
- JSON (для машинной обработки)
"""

import csv
import json
import os
from datetime import datetime
from typing import Any


class CredentialExporter:
    """
    Экспортёр учётных данных в различные форматы.

    Поддерживаемые форматы:
    - CSV (comma-separated values)
    - TXT (текстовый формат с разделителями)
    - JSON (для машинной обработки)
    """

    def __init__(self, output_dir: str = "output"):
        """
        Инициализация экспортёра.

        Args:
            output_dir: Директория для сохранения файлов
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _generate_filename(self, extension: str) -> str:
        """
        Генерация имени файла с временной меткой.

        Args:
            extension: Расширение файла

        Returns:
            Имя файла в формате credentials_YYYYMMDD_HHMMSS.ext
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"credentials_{timestamp}.{extension}"

    def export_csv(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт данных в CSV формат.

        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)

        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            filename = self._generate_filename("csv")

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

    def export_txt(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт данных в TXT формат (читаемый текстовый формат).

        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)

        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            filename = self._generate_filename("txt")

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

    def export_json(self, users: list[dict[str, Any]], filename: str | None = None) -> str:
        """
        Экспорт данных в JSON формат (для машинной обработки).

        Args:
            users: Список словарей с данными пользователей
            filename: Имя файла (по умолчанию генерируется автоматически)

        Returns:
            Путь к сохранённому файлу
        """
        if filename is None:
            filename = self._generate_filename("json")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_users': len(users),
                'users': users
            }, jsonfile, ensure_ascii=False, indent=2)

        return filepath
