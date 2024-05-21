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
        results = self.session.exec(
            select(
                Stage.stage,
                func.string_agg(StageSynonym.synonym, ', ').label('synonyms')
            )
            .join(StageSynonym)
            .where(Stage.org_group_id == org_group_id)
            .group_by(Stage.stage)
            .order_by(Stage.stage, StageSynonym.synonym)
        ).all()

        return results

    def get_or_create(self, org_group_id: int, stage: str):
        """Get existing record or create a new one."""
        stage = self.session.exec(
            select(Stage)
            .where(Stage.org_group_id == org_group_id)
            .where(Stage.stage == stage)
        ).one_or_none()

        if stage is None:
            # Create new.
            stage = Stage(
                org_group_id=org_group_id,
                stage=stage
            )

        return stage

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

    def get_code_lookup(self, org_group_id: int) -> {}:
        """Return a look up from stage to stage_synonym_id"""
        stage_synonyms = self.session.exec(
            select(StageSynonym)
            .where(StageSynonym.org_group_id == org_group_id)
        )

        stage_lookup = {}
        for stage_synonym in stage_synonyms:
            stage_lookup[stage_synonym.stage] = stage_synonym.id

        return stage_lookup

    def load_file(
            self, dir: str,
            org_group_id: int,
            rules_commit: str,
            file: str | None = None
    ):
        """Read a stage_synonyms file and save to database."""

        # Accumulate a list of errors.
        errors = []

        if file is None:
            file = self.default_file
        # Read the stage synonyms file into a dataframe.
        df = pd.read_csv(
            f'{dir}/{file}', dtype={'stage': str, 'synonyms': str}
        )

        for row in df.to_dict('records'):
            # Add or update the stage.
            stage = self.get_or_create(org_group_id, row['stage'])
            stage.commit = rules_commit
            self.session.add(stage)
            self.session.commit()

            # Add or update the synonyms.
            self.stage_synonym_repo.load(
                stage.id,
                row['synonyms'],
                rules_commit
            )

        # Delete out of date stage records.
        self.purge(org_group_id, rules_commit)

        return errors
