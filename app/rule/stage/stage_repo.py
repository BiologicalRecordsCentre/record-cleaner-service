import pandas as pd

from sqlmodel import select, func

from app.sqlmodels import Stage, StageSynonym

from ..rule_repo_base import RuleRepoBase
from .stage_synonym_repo import StageSynonymRepo


class StageRepo(RuleRepoBase):
    default_file = 'stage_synonyms.csv'

    def __init__(self, session):
        super().__init__(session)
        self.stage_synonym_repo = StageSynonymRepo(session)

    def list(self, org_group_id: int):
        """Return a list of stages for the org_group.

        Stages are listed in original sort order.
        Synonyms are aggregated and listed in alphabetical order.
        """
        results = self.session.exec(
            select(
                Stage.stage,
                func.group_concat(StageSynonym.synonym).label('synonyms')
            )
            .join(StageSynonym)
            .where(Stage.org_group_id == org_group_id)
            .group_by(Stage.stage)
            .order_by(Stage.sort_order)
        ).all()

        stages = []
        for stage, synonyms in results:
            stages.append({
                'stage': stage,
                'synonyms': synonyms
            })

        return stages

    def get_or_create(self, org_group_id: int, stage: str):
        """Get existing record or create a new one."""
        record = self.session.exec(
            select(Stage)
            .where(Stage.org_group_id == org_group_id)
            .where(Stage.stage == stage)
        ).one_or_none()

        if record is None:
            # Create new.
            record = Stage(
                org_group_id=org_group_id,
                stage=stage
            )

        return record

    def purge(self, org_group_id: int, rules_commit):
        """Delete records for org_group not from current commit."""
        stages = self.session.exec(
            select(Stage)
            .where(Stage.org_group_id == org_group_id)
            .where(Stage.commit != rules_commit)
        )
        for stage in stages:
            # Delete all synonyms of the stage we are purging.
            self.stage_synonym_repo.purge(stage.id)
            self.session.delete(stage)
        self.session.commit()

    def get_stage_lookup(self, org_group_id: int) -> dict:
        """Return a look up from stage to stage_id"""
        records = self.session.exec(
            select(Stage)
            .where(Stage.org_group_id == org_group_id)
        )

        stage_lookup = {}
        for record in records:
            stage_lookup[record.stage] = record.id

        return stage_lookup

    def load_file(
            self, dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read a stage_synonyms file and save to database.

        The data is split across two tables: Stage and StageSynonym.
        Each org_group may specify different stages for use in their rules.
        Each stage may have multiple synonyms."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the stage synonyms file into a dataframe.
        df = pd.read_csv(
            f'{dir}/{file}', dtype={'stage': str, 'synonyms': str}
        )

        for index, row in enumerate(df.to_dict('records')):
            # Add or update the stage.
            stage = row['stage'].strip().lower()
            record = self.get_or_create(org_group_id, stage)
            record.commit = rules_commit
            record.sort_order = index
            self.session.add(record)
            self.session.commit()

            # Add or update the synonyms.
            self.stage_synonym_repo.load(
                record.id,
                row['synonyms'],
                rules_commit
            )

        # Delete out of date stage records.
        self.purge(org_group_id, rules_commit)

        return errors
