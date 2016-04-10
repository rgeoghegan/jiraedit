from collections import OrderedDict

import jira
import tabulate

def user_string(user):
    if user is None:
        return "None"
    return "{} <{}>".format(user.displayName, user.emailAddress)

class JiraIssue:
    FIELD_ORDER = ['Assignee']

    def __init__(self, issue_id, config):
        self.client = jira.JIRA(
            server=config['server'],
            basic_auth=(config['username'], config['password']),
        )
        self.issue = self.client.issue(issue_id)
        self.serialized = self.serialize()

    def serialize(self):
        return {
            'Key': self.issue.key,
            'Summary': self.issue.fields.summary,
            'Assignee': user_string(self.issue.fields.assignee),
            'Description': self.issue.fields.description,
        }

    def __str__(self):
        text = []

        title = "{}: {}".format(
            self.serialized['Key'],
            self.serialized['Summary'],
        )
        text.append(title)
        underbar = '-' * len(title)
        text.append(underbar)
        text.append("")

        text.append(
            tabulate.tabulate(
                [(k + ":", self.serialized[k]) for k in self.FIELD_ORDER],
                tablefmt='plain',
            )
        )

        text.append("Description:")
        text.append("")
        text.append(self.serialized['Description'])

        return "\n".join(text)
