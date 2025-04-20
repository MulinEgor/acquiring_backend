from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from src.apps.permissions.schemas import PermissionGetSchema
from src.apps.requisites.schemas import RequisiteGetSchema
from src.core.database import Base
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class UserGetSchema(BaseModel):
    id: int
    email: EmailStr
    balance: int
    amount_frozen: int
    is_active: bool
    priority: int
    permissions: list[PermissionGetSchema]
    requisites: list[RequisiteGetSchema]
    is_2fa_enabled: bool

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj: dict | Base) -> "UserGetSchema":
        """
        Пользовательская валидация модели.

        Args:
            obj: Входные данные для валидации

        Returns:
            UserGetSchema: Валидированный объект схемы
        """
        if not isinstance(obj, dict):
            obj = obj.__dict__

        obj["permissions"] = [
            PermissionGetSchema.validate(user_permission.permission)
            for user_permission in obj["users_permissions"]
        ]

        return super(UserGetSchema, cls).model_validate(obj)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserCreateSchema(BaseModel):
    email: EmailStr
    priority: int = Field(default=0)
    permissions_ids: list[int]


class UserCreatedGetSchema(UserGetSchema):
    """Pydantic схема для получения созданного пользователя."""

    password: str


class UserCreateRepositorySchema(BaseModel):
    email: EmailStr
    priority: int
    hashed_password: str


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    priority: int | None = None
    permissions_ids: list[int] | None = None
    is_active: bool | None = None


class UserUpdateRepositorySchema(BaseModel):
    email: EmailStr | None = None
    hashed_password: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class UsersListGetSchema(DataListGetBaseSchema):
    data: list[UserGetSchema]


class UsersPaginationSchema(PaginationBaseSchema):
    id: int | None = None
    email: EmailStr | None = None
    priority: int | None = None
    permissions_ids: list[int] | None = None
    is_active: bool | None = None
    is_2fa_enabled: bool | None = None
