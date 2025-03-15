"""seeds

Revision ID: 91b745f5bf2c
Revises: 72657a81baf7
Create Date: 2025-03-15 12:11:27.138880+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from src.permissions.enums import PermissionEnum
from src.permissions.models import PermissionModel
from src.services.hash_service import HashService
from src.users.models import UserModel

# revision identifiers, used by Alembic.
revision: str = "91b745f5bf2c"
down_revision: Union[str, None] = "72657a81baf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for permission in PermissionEnum:
        op.execute(
            sa.insert(PermissionModel).values(
                name=permission.value,
            )
        )

    op.execute(
        sa.insert(UserModel).values(
            email="bopleromn@gmail.com",
            hashed_password=HashService.generate("admin"),
            is_2fa_enabled=True,
        )
    )


def downgrade() -> None:
    op.execute(sa.delete(PermissionModel))
    op.execute(sa.delete(UserModel))
