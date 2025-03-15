"""Модуль для перечислений разрешений."""

from enum import StrEnum


class PermissionEnum(StrEnum):
    """Перечисление разрешений."""

    # MARK: User
    GET_MY_USER = "получить своего пользователя"
    GET_USER = "получить пользователя"
    CREATE_USER = "создать пользователя"
    UPDATE_USER = "обновить пользователя"
    DELETE_USER = "удалить пользователя"

    # MARK: Permission
    GET_PERMISSION = "получить разрешение"
    CREATE_PERMISSION = "создать разрешение"
    UPDATE_PERMISSION = "обновить разрешение"
    DELETE_PERMISSION = "удалить разрешение"
