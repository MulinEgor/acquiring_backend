"""seeds

Revision ID: cd0c0d328985
Revises: 578db02b3c33
Create Date: 2025-03-18 09:07:51.575160+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op
from src.permissions.enums import PermissionEnum
from src.permissions.models import PermissionModel
from src.services.hash_service import HashService
from src.users.models import UserModel
from src.users_permissions.models import UsersPermissionsModel

# revision identifiers, used by Alembic.
revision: str = "cd0c0d328985"
down_revision: Union[str, None] = "578db02b3c33"
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

    for permission in PermissionEnum:
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
