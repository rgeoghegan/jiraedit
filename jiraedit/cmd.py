import argparse
import configparser
import os

from .issue import JiraIssue
from .testing import FakeJiraIssue

def parse_args():
    parser = argparse.ArgumentParser(
        description='Edit jira issues through the command line'
    )
    parser.add_argument(
        '-c', '--config', default='~/.jiraeditrc',
        help='Which config ini file to use (default %(default)s)'
    )
    parser.add_argument(
        'issue', help='Issue identifier to edit'
    )
    return parser.parse_args()


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(os.path.expandvars(config_path)))
    return config


def run():
    args = parse_args()
    config = read_config(args.config)

    issue = FakeJiraIssue(
        args.issue,
        config[config.sections()[0]]
    )
    print(issue)
