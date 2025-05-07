from typing import TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
PaginationSchemaType = TypeVar("PaginationSchemaType", bound=BaseModel)
GetListSchemaType = TypeVar("GetListSchemaType", bound=BaseModel)
