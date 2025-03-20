"""seeds

Revision ID: fa1720cfec9f
Revises: 4a144c9bb075
Create Date: 2025-03-20 09:14:32.508908+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op
from src.core import constants
from src.modules.permissions.models import PermissionModel
from src.modules.services.hash_service import HashService
from src.modules.users.models import UserModel
from src.modules.users_permissions.models import UsersPermissionsModel

# revision identifiers, used by Alembic.
revision: str = "fa1720cfec9f"
down_revision: Union[str, None] = "4a144c9bb075"
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
