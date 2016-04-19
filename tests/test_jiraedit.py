import unittest

from jiraedit.issue import (
    JiraIssue, ParseCaseTextException, JiraIssueConnection
)

EXAMPLE_ISSUE = {
    'key': 'CASE-42',
    'summary': 'Test issue, plz ignore',
    'Assignee': 'Misael Stehr <misael.stehr@example.com>',
    'Description': 'Quos alias quisquam inventore. \r\n\r\nDoloremque '
        'aperiam enim error ex nisi dolorem amet. Assumenda vero '
        'architecto dignissimos neque rerum corporis reprehenderit '
        'et.',
}

USERS = [
    {'email': 'ewell.runolfsdottir@zieme.com',
     'fullname': 'Ewell Runolfsdottir'},
    {'email': 'cayden.zemlak@herman.info',
     'fullname': 'Cayden Zemlak'},
    {'email': 'lacie.ratke@gutmann.com',
     'fullname': 'Lacie Ratke'},
    {'email': 'denton.swift@maggio-kulas.biz',
     'fullname': 'Denton Swift'},
]


class FakeIssueConnection:
    """Mock class mimicking a JiraIssueConnection."""
    def __init__(self, serialized=None):
        self.serialized = serialized or EXAMPLE_ISSUE

    def serialize(self):
        return self.serialized

    def valid_assignees(self):
        users = {}
        for u in USERS:
            username = (u['email']
                        if u['email'] != 'cayden.zemlak@herman.info'
                        else 'admin')
            
            active = u['email'] != 'lacie.ratke@gutmann.com'

            users[username] = {
                'active': active,
                'email': u['email'],
                'fullname': u['fullname']
            }

        return users


class TestPrinting(unittest.TestCase):
    def test_printing(self):
        issue = JiraIssue(FakeIssueConnection())
        text = str(issue).split('\n')

        self.assertTrue(text[0].startswith(
            EXAMPLE_ISSUE[JiraIssueConnection.KEY_NAME]
        ))


class TestParsing(unittest.TestCase):
    def test_simple_parsing(self):
        issue = JiraIssue(FakeIssueConnection())
        parsed = issue.parse(
            "CASE-42: Test issue, plz ignore\n"
            "-------------------------------\n"
            "\n"
            "Assignee: Misael Stehr <misael.stehr@example.com>\n"
            "\n"
            "Description:\n"
            "Quos alias quisquam inventore. \n\nDoloremque aperiam enim "
            "error ex nisi dolorem amet. Assumenda vero architecto "
            "dignissimos neque rerum corporis reprehenderit et.\n"
        )

        self.assertEqual(parsed, EXAMPLE_ISSUE)


class TestDifferences(unittest.TestCase):
    def test_different_title(self):
        parsed = EXAMPLE_ISSUE.copy()
        issue = JiraIssue(FakeIssueConnection())

        parsed[JiraIssueConnection.KEY_NAME] = 'CASE-43'

        self.assertRaises(ParseCaseTextException, issue.diff, parsed)

    def test_summary_change(self):
        parsed = EXAMPLE_ISSUE.copy()
        issue = JiraIssue(FakeIssueConnection())
        parsed['summary'] = 'Hello world'

        diff = issue.diff(parsed)
        self.assertEqual({
                'summary': (EXAMPLE_ISSUE['summary'], 'Hello world'),
            },
            diff
        )

    def test_description_change(self):
        parsed = EXAMPLE_ISSUE.copy()
        issue = JiraIssue(FakeIssueConnection())
        new_description = EXAMPLE_ISSUE['Description'] + '\nI love jira'
        parsed['Description'] = new_description

        diff = issue.diff(parsed)
        self.assertEqual({
                'Description': (EXAMPLE_ISSUE['Description'], new_description)
            },
            diff
        )
