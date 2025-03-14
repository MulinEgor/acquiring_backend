"""seeds

Revision ID: 8065b19d39f4
Revises: e9d73be9579a
Create Date: 2025-03-14 18:40:03.900339+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from src.permissions.enums import PermissionEnum
from src.permissions.models import PermissionModel

# revision identifiers, used by Alembic.
revision: str = "8065b19d39f4"
down_revision: Union[str, None] = "e9d73be9579a"
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
