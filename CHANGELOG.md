# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Env setting for phelology tolerance.
- Env setting for tenkm tolerance.

### Changed
- Message for phenology failures within tolerance.
- Message for tenkn failure within tolerance.

### Fixed
- Phenology test for records with long date range.

### Removed

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

### Fixed

### Removed
- id_difficulty from /validate response.
- ok from /verify and /validate response

## [1.0.0]

First release