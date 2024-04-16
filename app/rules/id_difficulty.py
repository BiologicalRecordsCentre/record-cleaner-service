import pandas as pd

from sqlmodel import Session, select

import app.species.cache as cache

from app.database import engine
from app.models import OrgGroup, Rule, DifficultyRule


class IdDifficulty:

    def __init__(self, tvk):
        """Load the id difficulty from the database."""
        with Session(engine) as session:
            statement = (select(Rule, DifficultyRule)
                         .join(DifficultyRule)
                         .where(Rule.preferred_tvk == tvk))
            results = session.exec(statement).one_or_none()
            if results is None:
                raise ValueError(
                    f'No identification difficulty found for {tvk}')
            rule, difficulty = results
            self.code = difficulty.code
            self.text = difficulty.text

    @classmethod
    def load_file(cls, organisation, group, dir, commit):
        """Read the id difficulty files, interpret, and save to database."""

        # Accumulate a list of errors.
        errors = []

        # Check for new OrgGroup.
        with Session(engine) as session:
            org_group = session.exec(
                select(OrgGroup)
                .where(OrgGroup.organisation == organisation)
                .where(OrgGroup.group == group)
            ).one_or_none()
            # Create if new.
            if org_group is None:
                org_group = OrgGroup(organisation=organisation, group=group)
                session.add(org_group)
                session.commit()

        # Read the difficulty codes file into a dataframe.
        codes = pd.read_csv(
            f'{dir}/difficulty_codes.csv'
        )
        # Find the maximum code value.
        if len(codes.index) == 0:
            # No records in file.
            max_code = 0
        else:
            max_code = codes['code'].max()

        # We need to keep a temporary lookup between code and id.
        code_to_id = [0] * (max_code + 1)

        # Save the difficulty rules in the database.
        with Session(engine) as session:
            for row in codes.to_dict('records'):
                # Check for new DifficultyRule.
                difficulty_rule = session.exec(
                    select(DifficultyRule)
                    .where(DifficultyRule.code == row['code'])
                    .where(DifficultyRule.org_group_id == org_group.id)
                ).one_or_none

                if difficulty_rule is None:
                    # Create if new.
                    difficulty_rule = DifficultyRule(
                        org_group_id=org_group.id,
                        code=row['code'],
                        text=row['text']
                    )
                else:
                    # Else update.
                    difficulty_rule.text = row['text']

                session.add(difficulty_rule)
                session.commit()
                code_to_id[difficulty_rule.code] = difficulty_rule.id

        # Read the id difficulty file into a dataframe.
        difficulties = pd.read_csv(
            f'{dir}/id_difficulty.csv'
        )

        # Save the species rule in the database.
        with Session(engine) as session:
            for row in difficulties.to_dict('records'):
                # Lookup preferred tvk.
                try:
                    taxon = cache.get_taxon_by_tvk(row['tvk'])
                except ValueError:
                    errors.append(f"Could not find taxon for {row['tvk']} "
                                  "in {organisation}/{group}/id_difficulty.csv")
                    continue

                # Check code is in limits
                if row['code'] > max_code or row['code'] < 1:
                    errors.append(f"Invalid code {row['code']} in "
                                  f"{organisation}/{group}/id_difficulty.csv")
                    continue

                preferred_tvk = taxon.preferred_tvk
                rule = Rule(
                    organisation=organisation,
                    group=group,
                    tvk=row['tvk'],
                    preferred_tvk=preferred_tvk,
                    name=row['taxon'],
                    difficulty_rule_id=code_to_id[row['code']]
                )
                session.add(rule)

            session.commit()
        return errors
