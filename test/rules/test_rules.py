import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.rules import rules
from app.rules.difficulty.difficulty_rule_repo import DifficultyRuleRepo
import app.species.cache as cache

from ..mocks import mock_make_search_request

client = TestClient(app)


class TestRules:

    @pytest.fixture(autouse=True)
    def set_rulesdir(self):
        # Override path to rulesdir.
        basedir = os.path.abspath(os.path.dirname(__file__))
        rules.rulesdir = os.path.join(basedir, 'testdata')

    def test_list_organisation_rules(self):
        organisation_groups_list = rules.list_organisation_groups()
        assert organisation_groups_list == [
            {'organisation1': ['group1', 'group2']},
            {'organisation2': ['group1']}
        ]

    def test_list_rules(self):
        rules_list = rules.list_rules()
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

    def test_load_database(self, mocker):
        # Mock the Indicia warehouse.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )
        rules.load_database()

        # assert IdDifficulty('NBNSYS0000008319').text == 'Easy'
        # assert IdDifficulty('NBNSYS0000008320').text == 'Moderate'
        # assert IdDifficulty('NBNSYS0000008323').text == 'Difficult'
        # assert IdDifficulty('NBNSYS0000008324').text == 'Very Difficult'
        # assert IdDifficulty('NBNSYS0000008325').text == 'Hard Very Difficult'
