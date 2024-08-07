def mock_make_search_request(params: dict) -> dict:

    if 'external_key' in params:
        match params['external_key']:
            case 'NBNSYS0000008319':
                return {'data': [{
                    'taxa_taxon_list_id': '4489',
                    'searchterm': 'Adalia bipunctata (Linnaeus, 1758)',
                    'original': 'Adalia bipunctata',
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
                    'original': 'Adalia decempunctata',
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
                    'original': 'Coccinella quinquepunctata',
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
                    'original': 'Coccinella septempunctata',
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
                    'original': 'Coccinella undecimpunctata',
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
                    'organism_key': 'NBNORG0000010519',
                    'taxon_group_id': '41',
                    'parent_id': '76113',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}
    elif 'searchQuery' in params:
        match params['searchQuery']:
            case 'Adalia bipunctata':
                return {'data': [{
                    'taxa_taxon_list_id': '4489',
                    'searchterm': 'Adalia bipunctata (Linnaeus, 1758)',
                    'original': 'Adalia bipunctata',
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
                    'organism_key': 'NBNORG0000010513',
                    'taxon_group_id': '41',
                    'parent_id': '4483',
                    'identification_difficulty': '1',
                    'id_diff_verification_rule_id': '1',
                    'taxon_rank': 'Species'
                }]}

    return {'data': []}
