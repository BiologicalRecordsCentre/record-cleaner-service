"""Replace taxon_id with organism_key in rules

Revision ID: 647d89048086
Revises: 5d19eaccf22e
Create Date: 2025-03-18 09:50:22.504282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '647d89048086'
down_revision: Union[str, None] = '5d19eaccf22e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('additionalrule') as batch_op:
        batch_op.add_column(
            sa.Column(
                'organism_key',
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False))
        batch_op.drop_index('ix_additionalrule_taxon_id')
        batch_op.drop_constraint(
            'uq_additionalrule_org_group_id', type_='unique')
        batch_op.create_unique_constraint(
            op.f('uq_additionalrule_org_group_id'),
            ['org_group_id', 'organism_key'])
        batch_op.create_index(
            op.f('ix_additionalrule_organism_key'),
            ['organism_key'],
            unique=False)
        batch_op.drop_constraint(
            'fk_additionalrule_taxon_id_taxon', type_='foreignkey')
        batch_op.drop_column('taxon_id')

    with op.batch_alter_table('difficultyrule') as batch_op:
        batch_op.add_column(
            sa.Column(
                'organism_key',
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False))
        batch_op.drop_index('ix_difficultyrule_taxon_id')
        batch_op.drop_constraint(
            'uq_difficultyrule_org_group_id', type_='unique')
        batch_op.create_unique_constraint(
            op.f('uq_difficultyrule_org_group_id'),
            ['org_group_id', 'organism_key', 'stage'])
        batch_op.create_index(
            op.f('ix_difficultyrule_organism_key'),
            ['organism_key'],
            unique=False)
        batch_op.drop_constraint(
            'fk_difficultyrule_taxon_id_taxon', type_='foreignkey')
        batch_op.drop_column('taxon_id')

    with op.batch_alter_table('periodrule') as batch_op:
        batch_op.add_column(
            sa.Column(
                'organism_key',
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False))
        batch_op.drop_index('ix_periodrule_taxon_id')
        batch_op.drop_constraint(
            'uq_periodrule_org_group_id', type_='unique')
        batch_op.create_unique_constraint(
            op.f('uq_periodrule_org_group_id'),
            ['org_group_id', 'organism_key'])
        batch_op.create_index(
            op.f('ix_periodrule_organism_key'),
            ['organism_key'],
            unique=False)
        batch_op.drop_constraint(
            'fk_periodrule_taxon_id_taxon', type_='foreignkey')
        batch_op.drop_column('taxon_id')

    with op.batch_alter_table('phenologyrule') as batch_op:
        batch_op.add_column(
            sa.Column(
                'organism_key',
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False))
        batch_op.drop_index('ix_phenologyrule_taxon_id')
        batch_op.drop_constraint(
            'uq_phenologyrule_org_group_id', type_='unique')
        batch_op.create_unique_constraint(
            op.f('uq_phenologyrule_org_group_id'),
            ['org_group_id', 'organism_key', 'stage_id'])
        batch_op.create_index(
            op.f('ix_phenologyrule_organism_key'),
            ['organism_key'],
            unique=False)
        batch_op.drop_constraint(
            'fk_phenologyrule_taxon_id_taxon', type_='foreignkey')
        batch_op.drop_column('taxon_id')

    with op.batch_alter_table('tenkmrule') as batch_op:
        batch_op.add_column(
            sa.Column(
                'organism_key',
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False))
        batch_op.drop_index('ix_tenkmrule_taxon_id')
        batch_op.drop_constraint(
            'uq_tenkmrule_org_group_id', type_='unique')
        batch_op.create_unique_constraint(
            op.f('uq_tenkmrule_org_group_id'),
            ['org_group_id', 'organism_key', 'km100'])
        batch_op.create_index(
            op.f('ix_tenkmrule_organism_key'),
            ['organism_key'],
            unique=False)
        batch_op.drop_constraint(
            'fk_tenkmrule_taxon_id_taxon', type_='foreignkey')
        batch_op.drop_column('taxon_id')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tenkmrule') as batch_op:
        batch_op.add_column(
            sa.Column('taxon_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(
            'fk_tenkmrule_taxon_id_taxon', 'taxon', ['taxon_id'], ['id'])
        batch_op.drop_index(op.f('ix_tenkmrule_organism_key'))
        batch_op.drop_constraint(
            op.f('uq_tenkmrule_org_group_id'), type_='unique')
        batch_op.create_unique_constraint(
            'uq_tenkmrule_org_group_id',
            ['org_group_id', 'taxon_id', 'km100'])
        batch_op.create_index(
            'ix_tenkmrule_taxon_id',
            ['taxon_id'],
            unique=False)
        batch_op.drop_column('organism_key')

    with op.batch_alter_table('phenologyrule') as batch_op:
        batch_op.add_column(
            sa.Column('taxon_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(
            'fk_phenologyrule_taxon_id_taxon', 'taxon', ['taxon_id'], ['id'])
        batch_op.drop_index(op.f('ix_phenologyrule_organism_key'))
        batch_op.drop_constraint(
            op.f('uq_phenologyrule_org_group_id'), type_='unique')
        batch_op.create_unique_constraint(
            'uq_phenologyrule_org_group_id',
            ['org_group_id', 'taxon_id', 'stage_id'])
        batch_op.create_index(
            'ix_phenologyrule_taxon_id',
            ['taxon_id'],
            unique=False)
        batch_op.drop_column('organism_key')

    with op.batch_alter_table('periodrule') as batch_op:
        batch_op.add_column(
            sa.Column('taxon_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(
            'fk_periodrule_taxon_id_taxon', 'taxon', ['taxon_id'], ['id'])
        batch_op.drop_index(op.f('ix_periodrule_organism_key'))
        batch_op.drop_constraint(
            op.f('uq_periodrule_org_group_id'), type_='unique')
        batch_op.create_unique_constraint(
            'uq_periodrule_org_group_id',
            ['org_group_id', 'taxon_id'])
        batch_op.create_index(
            'ix_periodrule_taxon_id',
            ['taxon_id'],
            unique=False)
        batch_op.drop_column('organism_key')

    with op.batch_alter_table('difficultyrule') as batch_op:
        batch_op.add_column(
            sa.Column('taxon_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(
            'fk_difficultyrule_taxon_id_taxon', 'taxon', ['taxon_id'], ['id'])
        batch_op.drop_index(op.f('ix_difficultyrule_organism_key'))
        batch_op.drop_constraint(
            op.f('uq_difficultyrule_org_group_id'), type_='unique')
        batch_op.create_unique_constraint(
            'uq_difficultyrule_org_group_id',
            ['org_group_id', 'taxon_id', 'stage'])
        batch_op.create_index(
            'ix_difficultyrule_taxon_id',
            ['taxon_id'],
            unique=False)
        batch_op.drop_column('organism_key')

    with op.batch_alter_table('additionalrule') as batch_op:
        batch_op.add_column(
            sa.Column('taxon_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(
            'fk_additionalrule_taxon_id_taxon', 'taxon', ['taxon_id'], ['id'])
        batch_op.drop_index(op.f('ix_additionalrule_organism_key'))
        batch_op.drop_constraint(
            op.f('uq_additionalrule_org_group_id'), type_='unique')
        batch_op.create_unique_constraint(
            'uq_additionalrule_org_group_id', ['org_group_id', 'taxon_id'])
        batch_op.create_index(
            'ix_additionalrule_taxon_id',
            ['taxon_id'],
            unique=False)
        batch_op.drop_column('organism_key')
