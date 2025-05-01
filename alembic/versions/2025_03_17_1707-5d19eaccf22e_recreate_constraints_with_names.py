"""Recreate constraints with names

Revision ID: 5d19eaccf22e
Revises: ee5121abc575
Create Date: 2025-03-17 17:07:12.947226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5d19eaccf22e'
down_revision: Union[str, None] = 'ee5121abc575'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First delete all tables with a constraint on them. We cannot alter them
    # as the constraints were created without a name.

    # Org group.
    op.drop_table('orggroup')
    # Stage
    op.drop_index('ix_stage_org_group_id', table_name='stage')
    op.drop_table('stage')
    # Stage synonym.
    op.drop_table('stagesynonym')
    # Difficulty code.
    op.drop_index('ix_difficultycode_org_group_id',
                  table_name='difficultycode')
    op.drop_table('difficultycode')
    # Difficulty rule.
    op.drop_index('ix_difficultyrule_difficulty_code_id',
                  table_name='difficultyrule')
    op.drop_index('ix_difficultyrule_org_group_id',
                  table_name='difficultyrule')
    op.drop_index('ix_difficultyrule_taxon_id', table_name='difficultyrule')
    op.drop_table('difficultyrule')
    # Additional code.
    op.drop_index('ix_additionalcode_org_group_id',
                  table_name='additionalcode')
    op.drop_table('additionalcode')
    # Additional rule.
    op.drop_index('ix_additionalrule_additional_code_id',
                  table_name='additionalrule')
    op.drop_index('ix_additionalrule_org_group_id',
                  table_name='additionalrule')
    op.drop_index('ix_additionalrule_taxon_id', table_name='additionalrule')
    op.drop_table('additionalrule')
    # Period rule.
    op.drop_index('ix_periodrule_org_group_id', table_name='periodrule')
    op.drop_index('ix_periodrule_taxon_id', table_name='periodrule')
    op.drop_table('periodrule')
    # Phenology rule.
    op.drop_index('ix_phenologyrule_org_group_id', table_name='phenologyrule')
    op.drop_index('ix_phenologyrule_stage_id', table_name='phenologyrule')
    op.drop_index('ix_phenologyrule_taxon_id', table_name='phenologyrule')
    op.drop_table('phenologyrule')
    # Tenkm rule.
    op.drop_index('ix_tenkmrule_org_group_id', table_name='tenkmrule')
    op.drop_index('ix_tenkmrule_taxon_id', table_name='tenkmrule')
    op.drop_table('tenkmrule')

    # Re-create tables - default names will now be applied to constraints.

    # Org group.
    op.create_table(
        'orggroup',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('organisation', sa.VARCHAR(), nullable=False),
        sa.Column('group', sa.VARCHAR(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.Column('stage_synonym_update', sa.VARCHAR(), nullable=True),
        sa.Column('additional_code_update', sa.VARCHAR(), nullable=True),
        sa.Column('additional_rule_update', sa.VARCHAR(), nullable=True),
        sa.Column('difficulty_code_update', sa.VARCHAR(), nullable=True),
        sa.Column('difficulty_rule_update', sa.VARCHAR(), nullable=True),
        sa.Column('period_rule_update', sa.VARCHAR(), nullable=True),
        sa.Column('phenology_rule_update', sa.VARCHAR(), nullable=True),
        sa.Column('tenkm_rule_update', sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organisation', 'group')
    )
    # Stage.
    op.create_table(
        'stage',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('stage', sa.VARCHAR(), nullable=False),
        sa.Column('sort_order', sa.INTEGER(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'stage')
    )
    op.create_index('ix_stage_org_group_id', 'stage',
                    ['org_group_id'], unique=False)
    # Stage synonym.
    op.create_table(
        'stagesynonym',
        sa.Column('stage_id', sa.INTEGER(), nullable=False),
        sa.Column('synonym', sa.VARCHAR(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['stage_id'], ['stage.id']),
        sa.PrimaryKeyConstraint('stage_id', 'synonym'),
        sa.UniqueConstraint('stage_id', 'synonym')
    )
    # Additional code.
    op.create_table(
        'additionalcode',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('code', sa.INTEGER(), nullable=False),
        sa.Column('text', sa.VARCHAR(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'code')
    )
    op.create_index('ix_additionalcode_org_group_id',
                    'additionalcode', ['org_group_id'], unique=False)
    # Additional rule.
    op.create_table(
        'additionalrule',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('taxon_id', sa.INTEGER(), nullable=False),
        sa.Column('additional_code_id', sa.INTEGER(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['additional_code_id'], ['additionalcode.id']),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'taxon_id')
    )
    op.create_index('ix_additionalrule_taxon_id',
                    'additionalrule', ['taxon_id'], unique=False)
    op.create_index('ix_additionalrule_org_group_id',
                    'additionalrule', ['org_group_id'], unique=False)
    op.create_index('ix_additionalrule_additional_code_id',
                    'additionalrule', ['additional_code_id'], unique=False)
    # Difficulty code.
    op.create_table(
        'difficultycode',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('code', sa.INTEGER(), nullable=False),
        sa.Column('text', sa.VARCHAR(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'code')
    )
    op.create_index('ix_difficultycode_org_group_id',
                    'difficultycode', ['org_group_id'], unique=False)
    # Difficulty rule.
    op.create_table(
        'difficultyrule',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('taxon_id', sa.INTEGER(), nullable=False),
        sa.Column('stage', sa.VARCHAR(), nullable=False),
        sa.Column('difficulty_code_id', sa.INTEGER(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['difficulty_code_id'], ['difficultycode.id']),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'taxon_id', 'stage')
    )
    op.create_index('ix_difficultyrule_taxon_id',
                    'difficultyrule', ['taxon_id'], unique=False)
    op.create_index('ix_difficultyrule_org_group_id',
                    'difficultyrule', ['org_group_id'], unique=False)
    op.create_index('ix_difficultyrule_difficulty_code_id',
                    'difficultyrule', ['difficulty_code_id'], unique=False)
    # Phenology rule.
    op.create_table(
        'phenologyrule',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('taxon_id', sa.INTEGER(), nullable=False),
        sa.Column('stage_id', sa.INTEGER(), nullable=False),
        sa.Column('start_day', sa.INTEGER(), nullable=False),
        sa.Column('start_month', sa.INTEGER(), nullable=False),
        sa.Column('end_day', sa.INTEGER(), nullable=False),
        sa.Column('end_month', sa.INTEGER(), nullable=False),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(
            ['org_group_id'], ['orggroup.id'], ),
        sa.ForeignKeyConstraint(['stage_id'], ['stage.id']),
        sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'taxon_id', 'stage_id')
    )
    op.create_index('ix_phenologyrule_taxon_id',
                    'phenologyrule', ['taxon_id'], unique=False)
    op.create_index('ix_phenologyrule_stage_id',
                    'phenologyrule', ['stage_id'], unique=False)
    op.create_index('ix_phenologyrule_org_group_id',
                    'phenologyrule', ['org_group_id'], unique=False)
    # Tenkm rule.
    op.create_table(
        'tenkmrule',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('taxon_id', sa.INTEGER(), nullable=False),
        sa.Column('km100', sa.VARCHAR(), nullable=True),
        sa.Column('km10', sa.VARCHAR(), nullable=True),
        sa.Column('coord_system', sa.VARCHAR(), nullable=True),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(
            ['org_group_id'], ['orggroup.id'], ),
        sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'taxon_id', 'km100')
    )
    op.create_index('ix_tenkmrule_taxon_id', 'tenkmrule',
                    ['taxon_id'], unique=False)
    op.create_index('ix_tenkmrule_org_group_id', 'tenkmrule',
                    ['org_group_id'], unique=False)

    op.create_table(
        'periodrule',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('org_group_id', sa.INTEGER(), nullable=False),
        sa.Column('taxon_id', sa.INTEGER(), nullable=False),
        sa.Column('start_date', sa.VARCHAR(), nullable=True),
        sa.Column('end_date', sa.VARCHAR(), nullable=True),
        sa.Column('commit', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['org_group_id'], ['orggroup.id']),
        sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_group_id', 'taxon_id')
    )
    op.create_index('ix_periodrule_taxon_id', 'periodrule',
                    ['taxon_id'], unique=False)
    op.create_index('ix_periodrule_org_group_id', 'periodrule',
                    ['org_group_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    pass
