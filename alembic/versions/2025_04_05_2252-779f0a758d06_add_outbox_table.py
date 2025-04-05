"""add outbox table

Revision ID: 779f0a758d06
Revises: 9a94af158891
Create Date: 2025-04-05 22:52:30.198086

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "779f0a758d06"
down_revision: Union[str, None] = "9a94af158891"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "outbox",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            sa.Enum("sent", "pending", "failed", name="status"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outbox")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("outbox")
