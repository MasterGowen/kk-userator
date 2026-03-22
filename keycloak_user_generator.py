#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
keycloak_user_generator.py

Обёртка для обратной совместимости.
Перенаправляет вызов в keycloak_userator.cli.main()

Автор: kk-userator project
Версия: 2.0.0
"""

import sys
from keycloak_userator.cli import main

if __name__ == '__main__':
    sys.exit(main())
