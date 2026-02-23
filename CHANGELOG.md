# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.2]

### Fixed
 - Failure updating rules.

### Changed
 - Rule updates to not git reset. This ensures only modified files are loaded.
 - Logging of rule files loaded.

## [3.0.1]

### Fixed
 - Unable to update rules from new branch.
 - Unable to update rules in maintenance mode.
 - Server error listing period rules with no end date.

## [3.0.0]

### Added
 - organism_key to Taxon table which is then included in responses from 
   /species/taxon_by_tvk and /species/taxon_by_name.
 - organism_key to response from /verify
 - End point /rules/additional/organism_key/{organism_key}
 - End point /rules/difficulty/organism_key/{organism_key}
 - End point /rules/period/organism_key/{organism_key}
 - End point /rules/phenology/organism_key/{organism_key}
 - End point /rules/tenkm/organism_key/{organism_key}

### Changed
 - Python module requirements to latest versions.
 - Rules to be referenced by organism key rather than taxon version key.
   Consequently this changes the response from 
    - /rules/additional/org_group/{org_group_id} 
    - /rules/difficulty/org_group/{org_group_id} 
    - /rules/period/org_group/{org_group_id} 
    - /rules/phenology/org_group/{org_group_id} 
    - /rules/tenkm/org_group/{org_group_id} 

### Fixed
 - Exception when Indicia API returned a JSON error.


## [2.1.0]

### Added
- Env setting for phelology tolerance.
- Env setting for tenkm tolerance.
- Verbose parameter to /verify endpoint

### Changed
- Message for phenology failures within tolerance.
- Message for tenkn failure within tolerance.

### Fixed
- Phenology test for records with long date range.
- Vice county assignment warning for Irish grid refs [#12](https://github.com/BiologicalRecordsCentre/record-cleaner-service/issues/12)
- Grid refs with spaces having type mis-identified.
- Vice county test passing any unknown grid ref.
- Vice county test failure for Irish grid refs [#13](https://github.com/BiologicalRecordsCentre/record-cleaner-service/issues/13)


## [2.0.0]

### Added
- This CHANGELOG file.
- End point county/code/{code}.
- End point county/gridref/{gridref}.
- id_difficulty to /verify response.
- result to /verify and /validate response. This contains a string of
  ['pass'|'warn'|'fail'].

### Changed
- /validate and /verify to raise errors on taxon name/tvk of ''.
- /validate to always returns sref.gridref.
- /validate to return vc assignment if vc not provided.
- /rules/update_result to have progress indicator, rules_updating_now.
- /verify id_difficulty to be an integer rather than a list. The highest value 
  rather than all values.
- /verify messages to include list of tests run.

### Removed
- id_difficulty from /validate response.
- ok from /verify and /validate response

## [1.0.0]

First release