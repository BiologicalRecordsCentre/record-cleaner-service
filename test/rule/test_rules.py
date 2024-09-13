import os
import pytest

from sqlmodel import Session

from app.rule.rule_repo import RuleRepo

from ..mocks import mock_env_settings


class TestRules:

    @pytest.fixture(name='env_settings')
    def set_rulesdir(self):
        env_settings = mock_env_settings()
        basedir = os.path.abspath(os.path.dirname(__file__))
        rulesdir = os.path.join(basedir, 'testdata')
        env_settings.rules_dir = rulesdir
        # Following required but not used.
        env_settings.rules_subdir = ''

        return env_settings

    def test_list_organisation_rules(self, session: Session, env_settings):
        repo = RuleRepo(session, env_settings)
        organisation_groups_list = repo.list_organisation_groups()
        assert organisation_groups_list == [
            {'organisation1': ['group1', 'group2']},
            {'organisation2': ['group1']}
        ]

    def test_list_rules(self, session: Session, env_settings):
        repo = RuleRepo(session, env_settings)
        rules_list = repo.list_rules()

        org1group1 = rules_list[0]['organisation1']['group1']
        assert 'Species Range' in org1group1
        assert 'Recording Period' in org1group1
        org1group2 = rules_list[0]['organisation1']['group2']
        assert 'Seasonal Period' in org1group2
        assert 'Additional Verification' in org1group2
        org2group1 = rules_list[1]['organisation2']['group1']
        assert 'Species Range' in org2group1
        assert 'Recording Period' in org2group1
        assert 'Seasonal Period' in org2group1
        assert 'Additional Verification' in org2group1

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
