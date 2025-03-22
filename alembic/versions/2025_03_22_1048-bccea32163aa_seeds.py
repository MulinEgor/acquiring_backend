"""seeds

Revision ID: bccea32163aa
Revises: 24622125207c
Create Date: 2025-03-22 10:48:19.930544+00:00

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
revision: str = "bccea32163aa"
down_revision: Union[str, None] = "24622125207c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    user = UserModel(
        email="admin@gmail.com",
        hashed_password=HashService.generate("admin"),
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

    session.commit()


def downgrade() -> None:
    op.execute(sa.delete(PermissionModel))
    op.execute(sa.delete(UserModel))
