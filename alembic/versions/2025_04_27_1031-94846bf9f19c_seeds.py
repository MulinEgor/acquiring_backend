"""seeds

Revision ID: 94846bf9f19c
Revises: 5b4f7a054f75
Create Date: 2025-04-27 10:31:51.821033+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op
from src.apps.permissions.model import PermissionModel
from src.apps.users.model import UserModel
from src.apps.users_permissions.model import UsersPermissionsModel
from src.core import constants
from src.lib.services.hash_service import HashService

# revision identifiers, used by Alembic.
revision: str = "94846bf9f19c"
down_revision: Union[str, None] = "5b4f7a054f75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    user = UserModel(
        email="admin@gmail.com",
        hashed_password=HashService.generate("admin"),
        balance=10000,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    for permission in constants.PermissionEnum:
        permission_model = PermissionModel(name=permission.value)
        session.add(permission_model)
        session.commit()
        session.refresh(permission_model)

        user_permission = UsersPermissionsModel(
            user_id=user.id,
            permission_id=permission_model.id,
        )
        session.add(user_permission)
        session.commit()

    user = UserModel(
        email="test@gmail.com",
        hashed_password=HashService.generate("test"),
    )

    session.add(user)
    session.commit()
    session.refresh(user)


def downgrade() -> None:
    op.execute(sa.delete(PermissionModel))
    op.execute(sa.delete(UserModel))
