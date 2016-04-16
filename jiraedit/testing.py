from .issue import JiraIssue

class FakeJiraIssue(JiraIssue):
    """
    Like JiraIssue, but instead of querying a jira server, uses fake data.
    """
    def __init__(self, issue_id, config):
        self.serialized = {
            'Key': 'CASE-42',
            'Summary': 'Test issue, plz ignore',
            'Assignee': 'Misael Stehr <misael.stehr@example.com>',
            'Description': 'Quos alias quisquam inventore. \n\nDoloremque '
                'aperiam enim error ex nisi dolorem amet. Assumenda vero '
                'architecto dignissimos neque rerum corporis reprehenderit '
                'et.',
        }

    def edit(self):
        text = """CASE-42: Test issue, plz ignore
-------------------------------

Assignee:  Bobby
Description:

Quos alias quisquam inventore. 

Doloremque aperiam enim error ex nisi dolorem amet. Assumenda vero architecto dignissimos neque rerum corporis reprehenderit et.
"""
        for n in self.parse_differences(text):
            print(n)
        return

