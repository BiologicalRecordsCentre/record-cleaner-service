import os
import shutil
import subprocess

import app.config as config

settings = config.get_settings()

basedir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(basedir, 'data')
gitdir = os.path.join(datadir, settings.rules_dir)
rulesdir = os.path.join(gitdir, settings.rules_subdir)


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
                    '--branch=' + settings.rules_branch,
                    '--depth=1',
                    '--filter=tree:0',
                    settings.rules_repo
                ],
                cwd=datadir
            )

            # Enable sparse checkout of just the rules folder.
            subprocess.check_call(
                [
                    'git',
                    'sparse-checkout',
                    'set',
                    settings.rules_subdir
                ],
                cwd=gitdir
            )

            # Checkout branch.
            subprocess.check_call(
                ['git', 'checkout', settings.rules_branch],
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


def list_society_groups():
    """Lists the rule groups based on the directory structure.

    Returns
    [
        {"society1": [group1, group2, ...]},
        {"society2": [group1, group2, ...]},
        ...
    ]
    """

    result = []

    # Top level folder is the society.
    societies = []
    for society in os.scandir(rulesdir):
        if society.is_dir():
            societies.append(society.name)
    societies.sort()

    # Second level folder is a group within the society.
    for idx, society in enumerate(societies):
        societydir = os.path.join(rulesdir, society)

        groups = []
        for group in os.scandir(societydir):
            if group.is_dir():
                groups.append(group.name)
        groups.sort()

        result.append({society: groups})

    return result


def list_rules():
    """Lists the rules types for society groups."""

    result = []

    society_groups_list = list_society_groups()

    for idx, society_groups in enumerate(society_groups_list):
        society, groups = society_groups.popitem()
        result.append({society: {}})

        for group in groups:
            groupdir = os.path.join(rulesdir, society, group)

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

        result[idx][society][group] = tests

    return result


def list_rule_folders():
    """Lists the folders in which rules are stored."""

    folders = []
    society_groups_list = list_society_groups()
    for society_groups in society_groups_list:
        society, groups = society_groups.popitem()
        for group in groups:
            groupdir = os.path.join(rulesdir, society, group)
            folders.append(groupdir)
