import datetime
import os
import shutil
import subprocess

from sqlmodel import Session, select

from app.database import engine
from app.settings import settings
from app.sqlmodels import OrgGroup


from .difficulty.difficulty_code_repo import DifficultyCodeRepo
from .difficulty.difficulty_rule_repo import DifficultyRuleRepo
from .org_group.org_group_repo import OrgGroupRepo
# from .id_difficulty import IdDifficulty

basedir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(basedir, 'data')
gitdir = os.path.join(datadir, settings.env.rules_dir)
rulesdir = os.path.join(gitdir, settings.env.rules_subdir)


def update():
    """Installs and updates our copy of the rules."""
    try:
        # Ensure data directory exists
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
    except OSError as e:
        e.add_note('Failed to create rules directory.')
        raise

    # Check git is installed.
    if not shutil.which('git'):
        raise Exception('Git is not installed')

    try:
        # Check repo has been cloned.
        if not os.path.isdir(gitdir):

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
                cwd=datadir
            )

            # Enable sparse checkout of just the rules folder.
            subprocess.check_call(
                [
                    'git',
                    'sparse-checkout',
                    'set',
                    settings.env.rules_subdir
                ],
                cwd=gitdir
            )

            # Checkout branch.
            subprocess.check_call(
                ['git', 'checkout', settings.env.rules_branch],
                cwd=gitdir
            )

        else:
            # Discard local changes (heaven forbid).
            subprocess.check_call(
                ['git', 'reset', '--hard', 'HEAD'],
                cwd=gitdir
            )
            # Pull latest changes.
            subprocess.check_call(
                ['git', 'pull'],
                cwd=gitdir
            )

        # Return current commit.
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=gitdir,
            text=True
        )
        return commit.strip()

    except subprocess.CalledProcessError as e:
        e.add_note('Failed to update rules.')
        raise
    except Exception as e:
        e.add_note('Unknown error trying to update rules.')
        raise Exception(e)


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


def load_database():
    """Loads the rule files in to the database."""

    organisation_groups_list = list_organisation_groups()
    for organisation_groups in organisation_groups_list:
        organisation, groups = organisation_groups.popitem()
        for group in groups:
            groupdir = os.path.join(rulesdir, organisation, group)
            org_group = OrgGroupRepo.get_or_create(organisation, group)
            rules_commit = settings.db.rules_commmit
            loading_time = datetime.datetime.now().isoformat()

            DifficultyCodeRepo.load_file(groupdir, org_group.id, rules_commit)
            org_group.difficulty_code_update = loading_time

            DifficultyRuleRepo.load_file(groupdir, org_group.id, rules_commit)
            org_group.difficulty_rule_update = loading_time

            # Save update times to OrgGroup record.
            with Session(engine) as session:
                session.add(org_group)
                session.commit()
