"""seeds

Revision ID: 8e38f9a191ae
Revises: 2bbd24611c6c
Create Date: 2025-03-14 18:51:45.496291+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from src.permissions.enums import PermissionEnum
from src.permissions.models import PermissionModel

# revision identifiers, used by Alembic.
revision: str = "8e38f9a191ae"
down_revision: Union[str, None] = "2bbd24611c6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for permission in PermissionEnum:
        op.execute(
            sa.insert(PermissionModel).values(
                name=permission.value,
            )
        )


def downgrade() -> None:
    op.execute(sa.delete(PermissionModel))
