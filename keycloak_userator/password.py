#!/usr/bin/env python3
"""
password.py

Генератор безопасных случайных паролей.

Требования:
- Минимум 6 символов
- Латинские буквы (строчные и заглавные)
- Цифры
"""

import secrets
import string

from keycloak_userator.config import Config


class PasswordGenerator:
    """
    Генератор безопасных случайных паролей.

    Требования:
    - Минимум 6 символов
    - Латинские буквы (строчные и заглавные)
    - Цифры
    """

    def __init__(self, config: Config):
        """
        Инициализация генератора паролей.

        Args:
            config: Конфигурация с параметрами генерации
        """
        self.length = config.password.length
        self.chars = self._build_char_set(config)

    def _build_char_set(self, config: Config) -> str:
        """
        Построение набора символов для генерации.

        Args:
            config: Конфигурация с параметрами

        Returns:
            Строка с допустимыми символами
        """
        chars = ""
        if config.password.use_lowercase:
            chars += string.ascii_lowercase
        if config.password.use_uppercase:
            chars += string.ascii_uppercase
        if config.password.use_digits:
            chars += string.digits
        if config.password.use_special:
            chars += string.punctuation

        # Если ни один набор не выбран, используем минимум
        if not chars:
            chars = string.ascii_letters + string.digits

        return chars

    def generate(self) -> str:
        """
        Генерация случайного пароля.

        Returns:
            Случайный пароль заданной длины
        """
        # Используем secrets для криптографически безопасной генерации
        return ''.join(secrets.choice(self.chars) for _ in range(self.length))

    def generate_batch(self, count: int) -> list[str]:
        """
        Генерация нескольких паролей.

        Args:
            count: Количество паролей для генерации

        Returns:
            Список сгенерированных паролей
        """
        return [self.generate() for _ in range(count)]
