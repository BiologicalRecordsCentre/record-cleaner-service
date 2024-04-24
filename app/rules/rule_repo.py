import datetime
import os
import shutil
import subprocess

from sqlmodel import Session, select

from app.settings import settings


from .additional.additional_code_repo import AdditionalCodeRepo
from .additional.additional_rule_repo import AdditionalRuleRepo
from .difficulty.difficulty_code_repo import DifficultyCodeRepo
from .difficulty.difficulty_rule_repo import DifficultyRuleRepo
from .org_group.org_group_repo import OrgGroupRepo
from .period.period_rule_repo import PeriodRuleRepo
from .tenkm.tenkm_rule_repo import TenkmRuleRepo


class RuleRepo:
    basedir = os.path.abspath(os.path.dirname(__file__))
    datadir = os.path.join(basedir, 'data')
    gitdir = os.path.join(datadir, settings.env.rules_dir)
    rulesdir = os.path.join(gitdir, settings.env.rules_subdir)

    def __init__(self, session):
        self.session = session

    def update(self):
        """Installs and updates our copy of the rules."""

        # Check semaphore to ensure only one update is happening at a time.
        if settings.db.rules_updating:
            raise Exception('Rules are already being updated.')

        # Set semaphore.
        settings.db.rules_updating = True

        # Keep a single update time for everything.
        self.loading_time = (
            datetime.datetime.now()
            .strftime('%Y-%m-%d %H:%M:%S')
        )

        try:
            self.rules_commit = self.git_update()
            results = self.db_update()
            results['commit'] = self.rules_commit
        except Exception:
            raise
        finally:
            # Always reset semaphore.
            settings.db.rules_updating = False

        return results

    def git_update(self):
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
            settings.db.rules_commmit = commit
            return commit

        except subprocess.CalledProcessError as e:
            e.add_note('Failed to update rules.')
            raise
        except Exception as e:
            e.add_note('Unknown error trying to update rules.')
            raise Exception(e)

    def db_update(self):
        """Loads the rule files in to the database."""

        ok = True
        data = []
        rule_types = [
            'Additional code',
            'Additional rule',
            'Difficulty code',
            'Difficulty rule',
            'Period rule',
            'Tenkm rule'
        ]

        # Load the rule directory structure.
        org_group_repo = OrgGroupRepo(self.session)
        org_group_repo.load_dir_structure(self.rulesdir, self.rules_commit)

        org_groups = org_group_repo.list()
        # Loop through all the organisation groups...
        for org_group in org_groups:
            group_errors = []

            for rule_type in rule_types:
                # Trying to load every rule type.
                errors = self.rule_file_update(rule_type, org_group)
                group_errors.extend(errors)

            if len(errors) > 0:
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

    def rule_file_update(self, rule_type, org_group):
        """Update rules of given type for given organisation group."""

        # Capitalise words, remove spaces, and append 'Repo'.
        repo_class_name = rule_type.title().replace(' ', '') + 'Repo'
        repo_class = globals()[repo_class_name]
        # Lower case words, substitute '_' for space, and append '_update'.
        update_field_name = rule_type.lower().replace(' ', '_') + '_update'

        organisation = org_group.organisation
        group = org_group.group
        groupdir = os.path.join(self.rulesdir, organisation, group)
        # Create an instance of the repository class.
        repo = repo_class(self.session)
        # Only update if there is a file and it has changed.
        file_updated = repo.file_updated(groupdir)
        if file_updated is None:
            return []
        rules_updated = getattr(org_group, update_field_name)
        if rules_updated and rules_updated >= file_updated:
            return []

        try:
            # Load the file in to the database.
            errors = repo.load_file(
                groupdir, org_group.id, self.rules_commit
            )
            # Save the update time.
            setattr(org_group, update_field_name, self.loading_time)
            self.session.add(org_group)
            self.session.commit()
        except Exception as e:
            errors = [str(e)]

        return errors


def list_organisation_groups():
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
    for organisation in os.scandir(rulesdir):
        if organisation.is_dir():
            organisations.append(organisation.name)
    organisations.sort()

    # Second level folder is a group within the organisation.
    for idx, organisation in enumerate(organisations):
        organisationdir = os.path.join(rulesdir, organisation)

        groups = []
        for group in os.scandir(organisationdir):
            if group.is_dir():
                groups.append(group.name)
        groups.sort()

        result.append({organisation: groups})

    return result


def list_rules():
    """Lists the rules types for organisation groups."""

    result = []

    organisation_groups_list = list_organisation_groups()

    for idx, organisation_groups in enumerate(organisation_groups_list):
        organisation, groups = organisation_groups.popitem()
        result.append({organisation: {}})

        for group in groups:
            groupdir = os.path.join(rulesdir, organisation, group)

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
