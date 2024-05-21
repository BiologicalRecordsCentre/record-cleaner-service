from sqlmodel import select

from app.sqlmodels import StageSynonym


class StageSynonymRepo:

    def __init__(self, session):
        self.session = session

    def get_or_create(self, stage_id: int, synonym: str):
        """Get existing record or create a new one."""
        synonym = self.session.exec(
            select(StageSynonym)
            .where(StageSynonym.stage_id == stage_id)
            .where(StageSynonym.synonym == synonym)
        ).one_or_none()

        if synonym is None:
            # Create new.
            synonym = StageSynonym(
                stage_id=stage_id,
                synonym=synonym
            )

        return synonym

    def purge(self, stage_id: int, rules_commit: str = None):
        stmt = select(StageSynonym).where(StageSynonym.stage_id == stage_id)
        if rules_commit is not None:
            stmt = stmt.where(StageSynonym.commit != rules_commit)

        synonyms = self.session.exec(stmt)

        for synonym in synonyms:
            self.session.delete(synonym)
        self.session.commit()

    def load(self, stage_id: int, synonyms: str, rules_commit: str):
        for synonym in synonyms.split(','):
            synonym = synonym.strip().lower()
            if synonym != '':
                stage_synonym = self.get_or_create(
                    stage_id, synonym
                )
                stage_synonym.commit = rules_commit
                self.session.add(stage_synonym)

        # Commit all the synonyms
        self.session.commit()

        # Delete out of date synonyms.
        self.purge(stage_id, rules_commit)
