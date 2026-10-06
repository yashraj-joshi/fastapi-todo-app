"""create phone number col on users table

Revision ID: 24f8f0c322e5
Revises: 
Create Date: 2026-06-16 15:10:22.855091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24f8f0c322e5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users",sa.Column("phone_number",sa.String(length=10),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users","phone_number")
