import datetime
import json
import logging
import os
import shutil
import subprocess
import threading
from typing import Optional, List

from app.sqlmodels import OrgGroup
from app.verify.verify_models import OrgGroupRules, Verified


from .additional.additional_code_repo import AdditionalCodeRepo
from .additional.additional_rule_repo import AdditionalRuleRepo
from .difficulty.difficulty_code_repo import DifficultyCodeRepo
from .difficulty.difficulty_rule_repo import DifficultyRuleRepo
from .org_group.org_group_repo import OrgGroupRepo
from .period.period_repo import PeriodRuleRepo
from .phenology.phenology_repo import PhenologyRuleRepo
from .stage.stage_repo import StageRepo
from .tenkm.tenkm_repo import TenkmRuleRepo

logger = logging.getLogger(f"uvicorn.{__name__}")


class RuleRepo:
    rule_file_types = [
        # A list of attributes for the file types we need to process with
        # each element having the following form:
        # {
        #     'name': A human readable name for error reporting.
        #     'class': The name of the repository class for the file type.
        #     'field': The name of the field in the OrgGroup table holding
        #         the timestamp of the last time the file was updated.
        # }
        {
            'name': 'Stage synonym',
            'class': StageRepo,
            'field': 'stage_synonym_update'
        },
        {
            'name': 'Additional code',
            'class': AdditionalCodeRepo,
            'field': 'additional_code_update'
        },
        {
            'name': 'Additional rule',
            'class': AdditionalRuleRepo,
            'field': 'additional_rule_update'
        },
        {
            'name': 'Difficulty code',
            'class': DifficultyCodeRepo,
            'field': 'difficulty_code_update'
        },
        {
            'name': 'Difficulty rule',
            'class': DifficultyRuleRepo,
            'field': 'difficulty_rule_update'
        },
        {
            'name': 'Period rule',
            'class': PeriodRuleRepo,
            'field': 'period_rule_update'
        },
        {
            'name': 'Period in year rule',
            'class': PhenologyRuleRepo,
            'field': 'phenology_rule_update'
        },
        {
            'name': 'Tenkm rule',
            'class': TenkmRuleRepo,
            'field': 'tenkm_rule_update'
        }
    ]

    # Dictionary of ules used for verification and their repo classes.
    # Difficulty is not a pass/fail and is done at validation.
    verification_rule_types = {
        'additional': AdditionalRuleRepo,
        'period': PeriodRuleRepo,
        'phenology': PhenologyRuleRepo,
        'tenkm': TenkmRuleRepo
    }

    def __init__(self, db, env_settings=False):
        self.db = db
        # When we instantiate the repo for running rules we don't need the
        # settings.
        if env_settings:
            self.basedir = os.path.abspath(os.path.dirname(__file__))
            self.datadir = os.path.join(self.basedir, 'data')
            self.gitdir = os.path.join(self.datadir, env_settings.rules_dir)
            self.rulesdir = os.path.join(
                self.gitdir, env_settings.rules_subdir)

    def update(self, settings, full: bool = False):
        """Installs and updates our copy of the rules."""

        # Check semaphore to ensure only one update is happening at a time.
        if settings.db.rules_updating:
            return {
                'ok': False,
                'data': "Rule update already in progress.",
                'commit': settings.db.rules_commit
            }

        # Set semaphore.
        settings.db.rules_updating = True

        # Start the update thread.
        thread = threading.Thread(
            target=self.update_thread, args=(settings, full))
        thread.start()

        # Return a response.
        return {
            'ok': True,
            'data': ("Rule update started. Use the update_result endpoint to "
                     "check results.")
        }

    def update_thread(self, settings, full: bool):
        """Performs the rule update in a thread."""

        # Keep a single update time for everything.
        self.loading_time = (
            datetime.datetime.now()
            .strftime('%Y-%m-%d %H:%M:%S')
        )

        logger.info("Rule update started.")

        try:
            self.rules_commit = self.git_update(settings)
            result = self.db_update(full)
            result['commit'] = self.rules_commit
            settings.db.rules_update_result = json.dumps(result)
            logger.info("Rule update complete.")
        except Exception as e:
            result = {
                'ok': False,
                'data': str(e),
                'commit': self.rules_commit
            }
            settings.db.rules_update_result = json.dumps(result)
            raise
        finally:
            # Always reset semaphore.
            settings.db.rules_updating = False

    def git_update(self, settings):
        """Installs and updates our copy of the rules."""
        try:
            # Ensure data directory exists
            if not os.path.isdir(self.datadir):
                os.mkdir(self.datadir)
        except OSError as e:
            e.add_note('Failed to create rules directory.')
            raise

        # Check git is installed.
        if not shutil.which('git'):
            raise Exception('Git is not installed')

        try:
            # Check repo has been cloned.
            if not os.path.isdir(self.gitdir):

                # Clone the repo without really getting anything much.
                subprocess.check_call(
                    [
                        'git',
                        'clone',
                        '--no-checkout',
                        '--branch=' + settings.env.rules_branch,
                        '--depth=1',
                        '--filter=tree:0',
                        settings.env.rules_repo
                    ],
                    cwd=self.datadir
                )

                # Enable sparse checkout of just the rules folder.
                subprocess.check_call(
                    [
                        'git',
                        'sparse-checkout',
                        'set',
                        settings.env.rules_subdir
                    ],
                    cwd=self.gitdir
                )

                # Checkout branch.
                subprocess.check_call(
                    ['git', 'checkout', settings.env.rules_branch],
                    cwd=self.gitdir
                )

            else:
                # Discard local changes (heaven forbid you'd make any).
                subprocess.check_call(
                    ['git', 'reset', '--hard', 'HEAD'],
                    cwd=self.gitdir
                )
                # Pull latest changes.
                subprocess.check_call(
                    ['git', 'pull'],
                    cwd=self.gitdir
                )

            # Get current commit.
            commit = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.gitdir,
                text=True
            ).strip()
            # Save it to settings and return it.
            settings.db.rules_commit = commit
            return commit

        except subprocess.CalledProcessError as e:
            e.add_note('Failed to update rules.')
            raise
        except Exception as e:
            e.add_note('Unknown error trying to update rules.')
            raise Exception(e)

    def db_update(self, full: bool = False):
        """Loads the rule files in to the database."""

        ok = True
        data = []

        # Load the rule directory structure.
        org_group_repo = OrgGroupRepo(self.db)
        org_group_repo.load_dir_structure(self.rulesdir, self.rules_commit)

        org_groups = org_group_repo.list()
        # Loop through all the organisation groups...
        for org_group in org_groups:
            group_errors = []

            for rule_type in self.rule_file_types:
                # Trying to load every rule file type.
                errors = self.rule_file_update(rule_type, org_group, full)
                if len(errors) > 0:
                    rule_name = rule_type['name']
                    group_errors.append({rule_name: errors})

            if len(group_errors) > 0:
                ok = False
            data.append({
                "organisation": org_group.organisation,
                "group": org_group.group,
                "errors": group_errors
            })

        return {
            "ok": ok,
            "data": data
        }

    def rule_file_update(
        self,
        rule_type: dict,
        org_group: OrgGroup,
        full: bool = False
    ):
        """Update rules of given type for given organisation group."""

        repo_class = rule_type['class']
        update_field_name = rule_type['field']
        organisation = org_group.organisation
        group = org_group.group
        groupdir = os.path.join(self.rulesdir, organisation, group)
        # Create an instance of the repository class.
        repo = repo_class(self.db)
        # Update if full = True or if the file has changed.
        if not full:
            file_updated = repo.file_updated(groupdir)
            if file_updated is None:
                # No file exists of this type for this organisation group.
                return []
            rules_updated = getattr(org_group, update_field_name)
            if rules_updated and rules_updated >= file_updated:
                # File has not been updated since last run.
                return []

        try:
            # Load the file in to the database.
            errors = repo.load_file(
                groupdir, org_group.id, self.rules_commit
            )
            # Save the update time.
            setattr(org_group, update_field_name, self.loading_time)
            self.db.add(org_group)
            self.db.commit()
        except FileNotFoundError:
            # It is not an error for a rule file to not exist.
            return []
        except Exception as e:
            errors = [str(e)]

        return errors

    def list_organisation_groups(self):
        """Lists the rule groups based on the directory structure.

        Returns
        [
            {"organisation1": [group1, group2, ...]},
            {"organisation2": [group1, group2, ...]},
            ...
        ]
        """

        result = []

        # Top level folder is the organisation.
        organisations = []
        for organisation in os.scandir(self.rulesdir):
            if organisation.is_dir():
                organisations.append(organisation.name)
        organisations.sort()

        # Second level folder is a group within the organisation.
        for idx, organisation in enumerate(organisations):
            organisationdir = os.path.join(self.rulesdir, organisation)

            groups = []
            for group in os.scandir(organisationdir):
                if group.is_dir():
                    groups.append(group.name)
            groups.sort()

            result.append({organisation: groups})

        return result

    def list_rules(self):
        """Lists the rules types for organisation groups."""

        result = []

        organisation_groups_list = self.list_organisation_groups()

        for idx, organisation_groups in enumerate(organisation_groups_list):
            organisation, groups = organisation_groups.popitem()
            result.append({organisation: {}})

            for group in groups:
                groupdir = os.path.join(self.rulesdir, organisation, group)

                # Rules are in files within the group folder.
                tests = []
                for file in os.scandir(groupdir):
                    match file.name:
                        case 'period.csv':
                            tests.append('Recording Period')
                        case 'periodwithinyear.csv':
                            tests.append('Seasonal Period')
                        case 'tenkm.csv':
                            tests.append('Species Range')
                        case 'additional.csv':
                            tests.append('Additional Verification')

                result[idx][organisation][group] = tests

        return result

    def run_rules(
        self,
        org_groups_rules_list: List[OrgGroupRules] | None,
        record: Verified
    ):
        """Run all the specified rules against the record."""
        repo = OrgGroupRepo(self.db)
        if org_groups_rules_list is None or len(org_groups_rules_list) == 0:
            # Use rules from all org_groups.
            self.run_rules_for_all(record)
        else:
            # Only use rules from listed org_groups.
            for org_group_rules in org_groups_rules_list:
                organisation = org_group_rules.organisation
                group = org_group_rules.group
                rules = org_group_rules.rules
                org_group = repo.get(organisation, group)
                if org_group is None:
                    raise ValueError(
                        "Unrecognised organisation:group, "
                        f"'{organisation}:{group}'."
                    )
                self.run_rules_for_org_group(org_group, rules, record)

        if len(record.messages) > 0:
            record.ok = False
            record.messages.sort()

    def run_rules_for_all(self, record: Verified):
        """Run all the rules against the record from all org_groups."""
        for rule_repo_class in self.verification_rule_types.values():
            repo = rule_repo_class(self.db)
            record.messages.extend(repo.run(record))

    def run_rules_for_org_group(
        self,
        org_group: OrgGroup,
        rules: Optional[List[str]],
        record: Verified
    ):
        """Run the rules against the record from a single org_group."""
        if rules is None:
            # Try all the rules
            for rule_repo_class in self.verification_rule_types.values():
                repo = rule_repo_class(self.db)
                record.messages.extend(repo.run(record, org_group.id))
        else:
            # Only use rules listed.
            for rule in rules:
                if rule not in self.verification_rule_types.keys():
                    # Not a valid rule type.
                    continue
                rule_repo_class = self.verification_rule_types[rule]
                repo = rule_repo_class(self.db)
                record.messages.extend(repo.run(record, org_group.id))
