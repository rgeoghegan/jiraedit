import argparse
import configparser
import os

from .issue import JiraIssue

def parse_args():
    parser = argparse.ArgumentParser(
        prog='jiraedit',
        description='Edit jira issues through the command line'
    )
    parser.add_argument(
        '-c', '--config', default='~/.jiraeditrc',
        help='Which config ini file to use (default %(default)s)'
    )
    parser.add_argument(
        '-p', '--print', action='store_true', dest='just_print',
        help='Instead of editing an issue, just print it to screen'
    )
    parser.add_argument(
        'issue', help='Issue identifier to edit'
    )
    return parser.parse_args()


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(os.path.expandvars(config_path)))
    return config


def edit_with_vim(filename):
    subprocess.check_call(['vim', filename])


def run():
    args = parse_args()
    config = read_config(args.config)

    # Use the first defined connection for now, we will add an argument to
    # pick different ones in the future.
    conn_config = config[config.sections()[0]]
    issue = JiraIssue.from_issue_id(conn_config, args.issue)

    if args.just_print:
        print(issue)
    else:
        # Right now, I just edit with vim, but in the future I'll make this
        # configurable.
        issue.edit(edit_with_vim)
