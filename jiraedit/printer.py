from collections import OrderedDict


class LineBuffer:
    """
    This class buffers the two next lines in a stream, so you can peek
    ahead for parsing.
    """
    def __init__(self, stream):
        self.stream = stream
        self.line_no = -1   # Since we call get_next_line() twice, the
                            # first line number will be 1
        self.next_line = None

        self.get_next_line()
        self.get_next_line()

    def get_next_line(self):
        self.current_line = self.next_line
        self.char_offset = 0
        self.line_no += 1

        try:
            self.next_line = next(self.stream)
        except StopIteration:
            self.next_line = None

        print("** current_line: {!r}".format(self.current_line))
        return self.current_line

    def end_of_file(self):
        return self.next_line != None

    def peek(self):
        if self.char_offset == len(self.current_line):
            self.next_line()
        return self.current_line[self.char_offset]

    def peek_line(self):
        return self.current_line[self.char_offset:]


class JiraParsingException(Exception):
    def __init__(self, line_no, raw_msg):
        self.line_no = line_no
        self.raw_msg = raw_msg
        super().__init__("(l. {}) {}".format(line_no, raw_msg))


#def split_by_colon(line):
#    a, b = line.split(':', 1)
#    return a.strip(), b.strip()


class JiraField:
    def __init__(self, name, label):
        self.name = name
        self.label = label

    def __str__(self):
        self.assert_bind()
        return "{}: {}".format(self.label, self.value())

    def value(self):
        self.assert_bind()
        return self.serialized[self.name]

    def bind(self, serialized):
        self.serialized = serialized

    def assert_bind(self):
        assert self.serialized is not None, \
                "Have you bound the field {} yet?".format(self)

    def parse(self, lines):
        self.assert_bind()
        label, value = self.parse_colon(lines)

        if label != self.label:
            raise JiraParsingException(
                "(l. {lineno}) Expecting '{label}: [{name}]', got {actual} "
                "instead.".format(
                    lineno=lines.line_no,
                    label=self.label,
                    name=self.name,
                    actual=label
                )
            )

        return value

    def parse_newline(self, lines):
        if lines.current_line != '\n':
            raise JiraParsingException(
                "Expecting newline after summary for {}, got {!r} "
                "instead.".format(
                    self, lines.current_line
                )
            )
        lines.get_next_line()

    def parse_colon(self, lines):
        try:
            a, b = lines.current_line.split(':', 1)
            lines.get_next_line()
            return a.strip(), b.strip()
        except ValueError:
            raise JiraParsingException(
                "(l. {line_no}) Expection [label]: [value], got {actual} "
                "instead.".format(
                    line_no=lines.line_no,
                    actual=lines.current_line
                )
            )


class JiraSummaryField(JiraField):
    def __init__(self, name):
        super().__init__(name, None)

    def __str__(self):
        self.assert_bind()
        texts = []
        title = "{}: {}".format(
            self.serialized['key'],
            self.value()
        )
        underbar = '-' * len(title)

        return "\n".join([
            title, underbar, ""
        ])

    def parse(self, lines):
        self.assert_bind()
        key, summary = self.parse_colon(lines)
        if key != self.serialized['key']:
            raise JiraParsingException(
                "Cannot change issue key, trying to set to {}".format(key)
            )

        if set(lines.current_line) != set(['-', '\n']):
            raise JiraParsingException(
                lines.line_no,
                "Expecting bar under summary for {}, got {!r} instead.".format(
                    self, lines.current_line
                )
            )
        lines.get_next_line()

        self.parse_newline(lines)

        return summary
        

class JiraDescription(JiraField):
    terminal = '=' * 10

    def __str__(self):
        self.assert_bind()
        return "\n".join(
            ["", "{}:".format(self.label), self.value(), self.terminal]
        )

    def parse(self, lines):
        self.assert_bind()
        self.parse_newline(lines)

        header = '{}:'.format(self.label)
        if lines.current_line.strip() != header:
            raise JiraParsingException(
                lines.line_no,
                "Expecting line {}, got {!r} instead.".format(
                    header, lines.current_line
                )
            )

        text = []
        while 1:
            line = lines.get_next_line()
            if line == None:
                raise JiraParsingException(
                    lines.line_no,
                    "Description block not terminated."
                )

            if set(line.strip()) == set(['=']):
                return "\r".join(text)

            text.append(line)


class JiraPrinter:
    def __init__(self, serialized):
        self.serialized = serialized
        self.fields = OrderedDict()

        for field in self.field_definitions():
            field.bind(self.serialized)
            self.fields[field.name] = field

    def field_definitions(self):
        return [
            JiraSummaryField('summary'),
            JiraField('Assignee', 'Assignee'),
            JiraDescription('Description', 'Description'),
        ]

    def __str__(self):
        output = []
        for field in self.fields.values():
            output.append(str(field))
        return "\n".join(output)

    def parse(self, stream):
        lines = LineBuffer(stream)

        output = OrderedDict()
        output['key'] = self.serialized['key']

        for field in self.fields.values():
            output[field.name] = field.parse(lines)

        return output
