"""Outbox

Revision ID: 1633711d1a9b
Revises: 662967a77aa3
Create Date: 2026-05-01 13:48:27.577281

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1633711d1a9b"
down_revision: Union[str, Sequence[str], None] = "662967a77aa3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
            CREATE TABLE IF NOT EXISTS outbox(
               id SERIAL PRIMARY KEY,
               payload JSONB NOT NULL,
               status VARCHAR(20) NOT NULL DEFAULT 'pending',
               created_at TIMESTAMP WITh TIME ZONE DEFAULT CURRENT_TIMESTAMP,
               processed_at TIMESTAMP WITH TIME ZONE,
               CONSTRAINT chk_outbox_status CHECK (status IN ('pending', 'sent'))
               )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
            DROP TABLE IF EXISTS outbox
        """
    )
