import tempfile
import subprocess

import jira
import tabulate

def user_string(user):
    if user is None:
        return "None"
    return "{} <{}>".format(user.displayName, user.emailAddress)


class ParseCaseTextException(Exception):
    pass

class JiraIssueConnection:
    KEY_NAME = 'key'

    def __init__(self, config, issue_id):
        self.client = jira.JIRA(
            server=config['server'],
            basic_auth=(config['username'], config['password']),
        )
        self.issue = self.client.issue(issue_id)

    def serialize(self):
        return {
            self.KEY_NAME: self.issue.key,
            'summary': self.issue.fields.summary,
            'Assignee': user_string(self.issue.fields.assignee),
            'Description': self.issue.fields.description,
        }


def split_by_colon(line):
    a, b = line.split(':', 1)
    return a.strip(), b.strip()


class JiraIssue:
    FIELD_ORDER = ['Assignee']

    def __init__(self, issue):
        self.issue = issue
        self.serialized = self.issue.serialize()

    @classmethod
    def from_issue_id(cls, config, issue_id):
        return cls(JiraIssueConnection(config, issue_id))

    def __str__(self):
        text = []

        title = "{}: {}".format(
            self.serialized[JiraIssueConnection.KEY_NAME],
            self.serialized['summary'],
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

        text.append("")
        text.append("Description:")
        text.append(self.serialized['Description'])

        return "\n".join(text)

    def edit(self):
        dump = tempfile.NamedTemporaryFile(delete=False)
        dump.write(str(self).encode('utf-8'))
        dump.close()

        subprocess.check_call(['vim', dump.name])

        with open(dump.name, 'r') as f:
            parsed = self.parse(f.read())
            for key, (orig, new) in self.diff(parsed).items():
                print("{}: {!r} -> {!r}".format(key, orig, new))

    def parse(self, text):
        lines = text.split('\n')

        issue_id, summary = split_by_colon(lines[0])
        output = {
            JiraIssueConnection.KEY_NAME: issue_id,
            'summary': summary,
        }
        
        if set(lines[1]) != set('-'):
            raise ParseCaseTextException(
                "Expecting underline on line #2, got {} instead".format(
                    lines[1]
                )
            )

        content_offset = 2
        if not lines[content_offset]:
            # Return line between title and content
            content_offset += 1

        for i, n in enumerate(self.FIELD_ORDER, content_offset): 
            title, value = split_by_colon(lines[i])
            if title != n:
                raise ParseCaseTextException(
                    "Expecting {} on line #{}, got {}.".format(n, i, title)
                )
            output[title] = value

        # Now for the description
        description_offset = len(self.FIELD_ORDER) + content_offset
        if not lines[description_offset].strip():
            description_offset += 1

        if lines[description_offset].strip() != 'Description:':
            raise ParseCaseTextException(
                "Expecting start of description on line #{}, got {}.".format(
                    i, lines[description_offset]
                )
            )

        # Collate description text, which uses windows return lines :(
        description = "\r\n".join(lines[description_offset+1:])
        output["Description"] = description.strip()

        return output

    def diff(self, new_values):
        original_keys = set(self.serialized.keys())

        if set(new_values.keys()) != original_keys:
            raise ParseCaseTextException(
                "Cannot add new attributes {} to case.".format(
                    new_values.difference(original_keys)
                )
            )

        original_keys.remove(JiraIssueConnection.KEY_NAME)
        new_key = new_values[JiraIssueConnection.KEY_NAME]
        if new_key != self.serialized[JiraIssueConnection.KEY_NAME]:
            raise ParseCaseTextException(
                "Cannot change key to {} of existing case.".format(new_key)
            )

        diff = {}
        for k in original_keys:
            if self.serialized[k] != new_values[k]:
                diff[k] = (self.serialized[k], new_values[k])

        return diff
