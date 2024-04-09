import os
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.rules import rules
from app.rules.id_difficulty import IdDifficulty

from ..mocks import mock_make_search_request

client = TestClient(app)


class TestRules:

    @pytest.fixture(autouse=True)
    def set_rulesdir(self):
        # Override path to rulesdir.
        basedir = os.path.abspath(os.path.dirname(__file__))
        rules.rulesdir = os.path.join(basedir, 'testdata')

    def test_list_society_rules(self):
        society_groups_list = rules.list_society_groups()
        assert society_groups_list == [
            {'society1': ['group1', 'group2']},
            {'society2': ['group1']}
        ]

    def test_list_rules(self):
        rules_list = rules.list_rules()
        assert rules_list == [
            {
                'society1': {
                    'group1': ['Species Range', 'Recording Period'],
                    'group2': ['Seasonal Period', 'Additional Verification']
                }
            },
            {
                'society2': {
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
        # Patch make_search_request with mock function.
        mocker.patch(
            'app.species.indicia.make_search_request',
            mock_make_search_request
        )

        rules.load_database()

        assert IdDifficulty('NBNSYS0000008319') == 'Easy'
        assert IdDifficulty('NBNSYS0000008320') == 'Moderate'
        assert IdDifficulty('NBNSYS0000008323') == 'Difficult'
        assert IdDifficulty('NBNSYS0000008324') == 'Very Difficult'
        assert IdDifficulty('NBNSYS0000008325') == 'Hard Very Difficult'
