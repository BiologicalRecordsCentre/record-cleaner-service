import os

import pandas as pd

from sqlmodel import Session

from app.database import engine
from app.models import Rule, DifficultyRule
from app.species.cache import get_taxon_by_tvk


class IdDifficulty:

    @classmethod
    def load_file(cls, scheme, group, rulesdir):
        """Read the id difficulty file and cache results."""

        folder = os.path.join(rulesdir, scheme, group)

        # Read the difficulty codes file into a dataframe.
        codes = pd.read_csv(
            f'{folder}/difficulty_codes.csv'
        )

        # We need to keep a temporary lookup between code and id.
        code_to_id = []

        # Cache the difficulty codes in the database.
        with Session(engine) as session:
            for row in codes.to_dict('records'):
                difficulty_rule = DifficultyRule(**row)
                session.add(difficulty_rule)
                session.commit()
                session.refresh(difficulty_rule)
                code_to_id[difficulty_rule.value_code] = difficulty_rule.id

        # Read the id difficulty file into a dataframe.
        difficulties = pd.read_csv(
            f'{folder}/id_difficulty.csv'
        )

        # Cache the difficulty codes in the database.
        with Session(engine) as session:
            for row in difficulties.to_dict('records'):
                # Lookup preferred tvk.
                preferred_tvk = get_taxon_by_tvk(row['tvk']).preferred_tvk

                rule = Rule(
                    scheme=scheme,
                    group=group,
                    tvk=row['tvk'],
                    preferred_tvk=preferred_tvk,
                    name=row['taxon'],
                    difficulty_rule_id=code_to_id[row['value_code']]
                )
                session.add(rule)

            session.commit()
