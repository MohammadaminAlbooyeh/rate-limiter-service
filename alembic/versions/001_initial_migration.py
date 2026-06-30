"""Initial migration: create all tables.

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", sa.String(), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("identity", sa.String(), nullable=False),
        sa.Column("algorithm", sa.String(), nullable=False),
        sa.Column("limit", sa.Integer(), nullable=False),
        sa.Column("window", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(), default="*"),
        sa.Column("tier", sa.String(), nullable=True),
    )

    op.create_table(
        "whitelist",
        sa.Column("identity", sa.String(), primary_key=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "blacklist",
        sa.Column("identity", sa.String(), primary_key=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("identity", sa.String(), nullable=False, index=True),
        sa.Column("current", sa.Integer(), nullable=False),
        sa.Column("limit", sa.Integer(), nullable=False),
        sa.Column("threshold", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "request_logs",
        sa.Column("id", sa.String(), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("identity", sa.String(), nullable=False, index=True),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True, index=True),
    )


def downgrade() -> None:
    op.drop_table("request_logs")
    op.drop_table("alerts")
    op.drop_table("blacklist")
    op.drop_table("whitelist")
    op.drop_table("rules")
