"""Модуль для маршрутов пользователей."""

from sanic import Blueprint, Request
from sanic_ext import openapi, validate

from src import dependencies
from src.responses import api_response
from src.users import schemas
from src.users.service import UserService

bp = Blueprint(
    "Users",
    url_prefix="/users",
)


# MARK: Get
@bp.get("/me")
@openapi.secured("Bearer")
@openapi.summary("Получить данные текущего пользователя.")
@openapi.response(
    status=200,
    description="Данные текущего пользователя",
    content=schemas.UserGetSchema,
)
async def get_current_user_route(
    request: Request,
):
    """
    Получить данные текущего пользователя.

    Требуется разрешение: `получить своего пользователя`.
    """
    user = await dependencies.get_current_user(request)
    return schemas.UserGetSchema.model_validate(user)


@bp.get("/<id:int>")
@openapi.summary("Получить данные пользователя по ID.")
@openapi.parameter(
    name="id",
    in_="path",
    required=True,
    description="ID пользователя",
)
@openapi.response(
    status=200,
    description="Данные пользователя",
    content=schemas.UserGetSchema,
)
async def get_user_by_id_route(
    request: Request,
    id: int,
):
    """
    Получить данные пользователя по ID.

    Требуется разрешение: `получить пользователя`.
    """
    async with request.ctx.get_db_session() as session:
        return api_response(await UserService.get_by_id(session, id))


@bp.get("")
@openapi.summary("Получить список пользователей")
@openapi.parameter(
    name="query",
    in_="query",
    type="object",
    schema=schemas.UsersPaginationSchema,
)
@openapi.response(
    status=200,
    description="Список пользователей",
    content=schemas.UsersListGetSchema,
)
@validate(query=schemas.UsersPaginationSchema)
async def get_users_by_admin_route(
    request: Request, query: schemas.UsersPaginationSchema
):
    """
    Получить список пользователей.

    Требуется разрешение: `получить пользователя`.
    """
    async with request.ctx.get_db_session() as session:
        return api_response(await UserService.get_all(session, query))


# MARK: Post
@bp.post("")
@openapi.summary("Создать нового пользователя.")
@openapi.body(
    description="Данные для создания пользователя",
    content=schemas.UserCreateSchema,
    validate=True,
)
@openapi.response(
    status=201,
    description="Данные созданного пользователя",
    content=schemas.UserGetSchema,
)
async def create_user_by_admin_route(
    request: Request,
    body: schemas.UserCreateSchema,
):
    """
    Создать нового пользователя.

    Требуется разрешение: `создать пользователя`.
    """
    async with request.ctx.get_db_session() as session:
        return api_response(
            await UserService.create(session, body),
            status=201,
        )


# MARK: Put
@bp.put("/<id:int>")
@openapi.summary("Обновить данные пользователя.")
@openapi.body(
    description="Данные для обновления пользователя",
    content=schemas.UserUpdateSchema,
    validate=True,
)
@openapi.response(
    status=202,
    description="Данные обновленного пользователя",
    content=schemas.UserGetSchema,
)
async def update_user_by_admin_route(
    request: Request,
    id: int,
    body: schemas.UserUpdateSchema,
):
    """
    Обновить данные пользователя.

    Требуется разрешение: `обновить пользователя`.
    """
    async with request.ctx.get_db_session() as session:
        return api_response(
            await UserService.update(session, id, body),
            status=202,
        )


# MARK: Delete
@bp.delete("/<id:int>")
@openapi.summary("Удалить пользователя.")
@openapi.response(
    status=204,
    description="Пользователь удален",
)
async def delete_user_by_admin_route(
    request: Request,
    id: int,
):
    """
    Удалить пользователя.

    Требуется разрешение: `удалить пользователя`.
    """
    async with request.ctx.get_db_session() as session:
        await UserService.delete(session, id)
