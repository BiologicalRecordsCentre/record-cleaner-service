
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.settings_env import EnvSettings
from app.settings_db import DbSettings


def mock_make_search_request(env: EnvSettings, params: dict) -> dict:

    if 'search_code' in params:
        match params['search_code']:
            case 'NBNSYS0000008319':
                return {'data': [{
                    'taxa_taxon_list_id': '4489',
                    'searchterm': 'Adalia bipunctata (Linnaeus, 1758)',
                    'taxon': 'Adalia bipunctata',
                    'authority': '(Linnaeus, 1758)',
                    'language_iso': 'lat',
                    'preferred_taxon': 'Adalia bipunctata',
                    'preferred_authority': '(Linnaeus, 1758)',
                    'default_common_name': '2-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '4489',
                    'taxon_meaning_id': '1974',
                    'external_key': 'NBNSYS0000008319',
                    'search_code': 'NBNSYS0000008319',
                    'organism_key': 'NBNORG0000010513',
                    'taxon_group_id': '41',
                    'parent_id': '4483',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'NBNSYS0000008320':
                return {'data': [{
                    'taxa_taxon_list_id': '4493',
                    'searchterm': 'Adalia decempunctata (Linnaeus, 1758)',
                    'taxon': 'Adalia decempunctata',
                    'authority': '(Linnaeus, 1758)',
                    'language_iso': 'lat',
                    'preferred_taxon': 'Adalia decempunctata',
                    'preferred_authority': '(Linnaeus, 1758)',
                    'default_common_name': '10-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '4493',
                    'taxon_meaning_id': '1975',
                    'external_key': 'NBNSYS0000008320',
                    'search_code': 'NBNSYS0000008320',
                    'organism_key': 'NBNORG0000010514',
                    'taxon_group_id': '41',
                    'parent_id': '4483',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'NBNSYS0000008323':
                return {'data': [{
                    'taxa_taxon_list_id': '76130',
                    'searchterm': 'Coccinella quinquepunctata Linnaeus, 1758',
                    'taxon': 'Coccinella quinquepunctata',
                    'authority': 'Linnaeus, 1758', 'language_iso': 'lat',
                    'preferred_taxon': 'Coccinella quinquepunctata',
                    'preferred_authority': 'Linnaeus, 1758',
                    'default_common_name': '5-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '76130',
                    'taxon_meaning_id': '27103',
                    'external_key': 'NBNSYS0000008323',
                    'search_code': 'NBNSYS0000008323',
                    'organism_key': 'NBNORG0000010517',
                    'taxon_group_id': '41',
                    'parent_id': '76113',
                    'identification_difficulty': '3',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'NBNSYS0000008324':
                return {'data': [{
                    'taxa_taxon_list_id': '76131',
                    'searchterm': 'Coccinella septempunctata Linnaeus, 1758',
                    'taxon': 'Coccinella septempunctata',
                    'authority': 'Linnaeus, 1758',
                    'language_iso': 'lat',
                    'preferred_taxon': 'Coccinella septempunctata',
                    'preferred_authority': 'Linnaeus, 1758',
                    'default_common_name': '7-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '76131',
                    'taxon_meaning_id': '27104',
                    'external_key': 'NBNSYS0000008324',
                    'search_code': 'NBNSYS0000008324',
                    'organism_key': 'NBNORG0000010518',
                    'taxon_group_id': '41',
                    'parent_id': '76113',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'NBNSYS0000008325':
                return {'data': [{
                    'taxa_taxon_list_id': '76134',
                    'searchterm': 'Coccinella undecimpunctata Linnaeus, 1758',
                    'taxon': 'Coccinella undecimpunctata',
                    'authority': 'Linnaeus, 1758',
                    'language_iso': 'lat',
                    'preferred_taxon': 'Coccinella undecimpunctata',
                    'preferred_authority': 'Linnaeus, 1758',
                    'default_common_name': '11-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '76134',
                    'taxon_meaning_id': '27106',
                    'external_key': 'NBNSYS0000008325',
                    'search_code': 'NBNSYS0000008325',
                    'organism_key': 'NBNORG0000010519',
                    'taxon_group_id': '41',
                    'parent_id': '76113',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'NBNSYS0000171481':
                return {'data': [{
                    'taxa_taxon_list_id': 350135,
                    'searchterm': 'Two-Spot Ladybird',
                    'taxon': 'Two-Spot Ladybird',
                    'language_iso': 'eng',
                    'preferred_taxon': 'Adalia bipunctata',
                    'preferred_authority': '(Linnaeus, 1758)',
                    'default_common_name': '2-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 'f',
                    'preferred_taxa_taxon_list_id': 4489,
                    'taxon_meaning_id': 1974,
                    'external_key': 'NBNSYS0000008319',
                    'search_code': 'NBNSYS0000171481',
                    'organism_key': 'NBNORG0000010513',
                    'taxon_group_id': 41,
                    'parent_id': 4483,
                    'taxon_rank': 'Species'
                }]}
    elif 'searchQuery' in params:
        match params['searchQuery']:
            case 'Adalia bipunctata':
                return {'data': [{
                    'taxa_taxon_list_id': '4489',
                    'searchterm': 'Adalia bipunctata (Linnaeus, 1758)',
                    'taxon': 'Adalia bipunctata',
                    'authority': '(Linnaeus, 1758)',
                    'language_iso': 'lat',
                    'preferred_taxon': 'Adalia bipunctata',
                    'preferred_authority': '(Linnaeus, 1758)',
                    'default_common_name': '2-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 't',
                    'preferred_taxa_taxon_list_id': '4489',
                    'taxon_meaning_id': '1974',
                    'external_key': 'NBNSYS0000008319',
                    'search_code': 'NBNSYS0000008319',
                    'organism_key': 'NBNORG0000010513',
                    'taxon_group_id': '41',
                    'parent_id': '4483',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
            case 'Two-Spot Ladybird':
                return {'data': [{
                    'taxa_taxon_list_id': 350135,
                    'searchterm': 'Two-Spot Ladybird',
                    'taxon': 'Two-Spot Ladybird',
                    'language_iso': 'eng',
                    'preferred_taxon': 'Adalia bipunctata',
                    'preferred_authority': '(Linnaeus, 1758)',
                    'default_common_name': '2-spot Ladybird',
                    'taxon_group': 'insect - beetle (Coleoptera)',
                    'preferred': 'f',
                    'preferred_taxa_taxon_list_id': 4489,
                    'taxon_meaning_id': 1974,
                    'external_key': 'NBNSYS0000008319',
                    'search_code': 'NBNSYS0000171481',
                    'organism_key': 'NBNORG0000010513',
                    'taxon_group_id': 41,
                    'parent_id': 4483,
                    'taxon_rank': 'Species'
                }]}

    # Response when no matches.
    return {'data': []}


def mock_env_settings() -> object:
    class MockEnvSettings(BaseSettings):
        # These default settings may get overriden if already in environment.
        # VS Code, for example, will load a .env file if it exists.
        jwt_key: str = '8f4e5dc18c0bc185c71f889ece4250210cbc76517a8b7d24cd3959b42e501a50'
        jwt_algorithm: str = 'HS256'
        jwt_expires_minutes: int = 15
        rules_repo: str = 'rules_repo'
        rules_branch: str = 'rules_branch'
        rules_dir: str = 'rules_dir'
        rules_subdir: str = 'rules_subdir'
        initial_user_name: str = 'root'
        initial_user_pass: str = 'pass'
        log_level: str = 'info'
        data_dir: str = '.'
        phenology_tolerance: int = 0
        tenkm_tolerance: int = 0

        # Freeze the settings so that tests are consistent with runtime config.
        model_config = SettingsConfigDict(frozen=True)

    env = MockEnvSettings()
    return env


def mock_env_tolerant_settings() -> object:
    class MockEnvTolerantSettings(BaseSettings):
        # These default settings may get overriden if already in environment.
        # VS Code, for example, will load a .env file if it exists.
        jwt_key: str = '8f4e5dc18c0bc185c71f889ece4250210cbc76517a8b7d24cd3959b42e501a50'
        jwt_algorithm: str = 'HS256'
        jwt_expires_minutes: int = 15
        rules_repo: str = 'rules_repo'
        rules_branch: str = 'rules_branch'
        rules_dir: str = 'rules_dir'
        rules_subdir: str = 'rules_subdir'
        initial_user_name: str = 'root'
        initial_user_pass: str = 'pass'
        log_level: str = 'info'
        phenology_tolerance: int = 7
        tenkm_tolerance: int = 1

        # Freeze the settings so that tests are consistent with runtime config.
        model_config = SettingsConfigDict(frozen=True)

    env = MockEnvTolerantSettings()
    return env


def mock_create_db(env: EnvSettings):
    # Creates an in-memory SQLite database
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    return engine


def mock_settings(engine, env: EnvSettings):
    # Creates a settings object with the test database engine.
    class MockSettings():
        def __init__(self, engine, env):
            self.env = env
            self.db = DbSettings(engine)

    settings = MockSettings(engine, env)
    return settings
