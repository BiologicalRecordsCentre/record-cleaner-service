from sqlmodel import Session, select

from app.sqlmodels import StageSynonym


class StageSynonymRepo:

    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, stage_id: int, synonym: str):
        """Get existing record or create a new one."""
        synonym_record = self.db.exec(
            select(StageSynonym)
            .where(StageSynonym.stage_id == stage_id)
            .where(StageSynonym.synonym == synonym)
        ).one_or_none()

        if synonym_record is None:
            # Create new.
            synonym_record = StageSynonym(
                stage_id=stage_id,
                synonym=synonym
            )

        return synonym_record

    def purge(self, stage_id: int, rules_commit: str = None):
        stmt = select(StageSynonym).where(StageSynonym.stage_id == stage_id)
        if rules_commit is not None:
            stmt = stmt.where(StageSynonym.commit != rules_commit)

        synonyms = self.db.exec(stmt)

        for synonym in synonyms:
            self.db.delete(synonym)
        self.db.commit()

    def load(self, stage_id: int, synonyms: str, rules_commit: str):
        for synonym in synonyms.split(','):
            synonym = synonym.strip().lower()
            if synonym != '':
                stage_synonym = self.get_or_create(
                    stage_id, synonym
                )
                stage_synonym.commit = rules_commit
                self.db.add(stage_synonym)

        # Commit all the synonyms
        self.db.commit()

        # Delete out of date synonyms.
        self.purge(stage_id, rules_commit)
