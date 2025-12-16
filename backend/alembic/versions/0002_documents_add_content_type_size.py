"""add documents content_type and size_bytes

Revision ID: 0002_doc_meta
Revises: 0001_init
Create Date: 2025-12-16

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_doc_meta"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("content_type", sa.String(length=128), nullable=True))
    op.add_column("documents", sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("documents", "size_bytes", server_default=None)


def downgrade() -> None:
    op.drop_column("documents", "size_bytes")
    op.drop_column("documents", "content_type")
