import os
import pytest

from sqlmodel import Session

from app.rules.rule_repo import RuleRepo

from ..mocks import mock_make_search_request


class TestRules:

    @pytest.fixture(autouse=True)
    def set_rulesdir(self):
        # Override path to rulesdir.
        basedir = os.path.abspath(os.path.dirname(__file__))
        RuleRepo.rulesdir = os.path.join(basedir, 'testdata')

    def test_list_organisation_rules(self, session: Session):
        repo = RuleRepo(session)
        organisation_groups_list = repo.list_organisation_groups()
        assert organisation_groups_list == [
            {'organisation1': ['group1', 'group2']},
            {'organisation2': ['group1']}
        ]

    def test_list_rules(self, session: Session):
        repo = RuleRepo(session)
        rules_list = repo.list_rules()
        assert rules_list == [
            {
                'organisation1': {
                    'group1': ['Species Range', 'Recording Period'],
                    'group2': ['Seasonal Period', 'Additional Verification']
                }
            },
            {
                'organisation2': {
                    'group1': [
                        'Species Range',
                        'Recording Period',
                        'Seasonal Period',
                        'Additional Verification'
                    ]
                }
            }
        ]

    # def test_load_database(self, mocker):
    #     # Mock the Indicia warehouse.
    #     mocker.patch(
    #         'app.species.indicia.make_search_request',
    #         mock_make_search_request
    #     )
    #     rule_repo.db_update()

    #     # assert IdDifficulty('NBNSYS0000008319').text == 'Easy'
    #     # assert IdDifficulty('NBNSYS0000008320').text == 'Moderate'
    #     # assert IdDifficulty('NBNSYS0000008323').text == 'Difficult'
    #     # assert IdDifficulty('NBNSYS0000008324').text == 'Very Difficult'
    #     # assert IdDifficulty('NBNSYS0000008325').text == 'Hard Very Difficult'
