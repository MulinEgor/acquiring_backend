"""seeds

Revision ID: c071466af0a9
Revises: 093b43e99305
Create Date: 2025-03-20 20:58:26.049517+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op
from src.apps.permissions.models import PermissionModel
from src.apps.users.models import UserModel
from src.apps.users_permissions.models import UsersPermissionsModel
from src.core import constants
from src.lib.services.hash_service import HashService

# revision identifiers, used by Alembic.
revision: str = "c071466af0a9"
down_revision: Union[str, None] = "093b43e99305"
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
