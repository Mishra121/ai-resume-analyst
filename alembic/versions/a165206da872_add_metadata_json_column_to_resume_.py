"""add metadata json column to resume_chunks

Revision ID: a165206da872
Revises: 679265dbec31
Create Date: 2025-12-29 13:26:12.046462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'a165206da872'
down_revision: Union[str, Sequence[str], None] = '679265dbec31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "resume_chunks",
        sa.Column(
            "meta_data",
            JSONB,        
            nullable=True,
            server_default=sa.text("'{}'::jsonb")
        )
    )

    op.alter_column(
        "resume_chunks",
        "meta_data",
        server_default=None
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("resume_chunks", "meta_data")

