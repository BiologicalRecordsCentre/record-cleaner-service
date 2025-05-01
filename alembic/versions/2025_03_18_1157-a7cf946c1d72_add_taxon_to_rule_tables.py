"""Add taxon to rule tables

Revision ID: a7cf946c1d72
Revises: 647d89048086
Create Date: 2025-03-18 11:57:54.230301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a7cf946c1d72'
down_revision: Union[str, None] = '647d89048086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('additionalrule', sa.Column(
        'taxon', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('difficultyrule', sa.Column(
        'taxon', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('periodrule', sa.Column(
        'taxon', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('phenologyrule', sa.Column(
        'taxon', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('tenkmrule', sa.Column(
        'taxon', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tenkmrule', 'taxon')
    op.drop_column('phenologyrule', 'taxon')
    op.drop_column('periodrule', 'taxon')
    op.drop_column('difficultyrule', 'taxon')
    op.drop_column('additionalrule', 'taxon')
