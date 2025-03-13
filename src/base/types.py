"""Модуль для базовых TypeVar типов данных, который используются в пакете src/base."""

from typing import TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
GetQuerySchemaType = TypeVar("GetQuerySchemaType", bound=BaseModel)
GetListSchemaType = TypeVar("GetListSchemaType", bound=BaseModel)
