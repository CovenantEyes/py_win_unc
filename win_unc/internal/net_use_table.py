"""
Contains functions and classes for parsing and storing the results of a `net use` command on
Windows. This table describes what the mounted UNC paths.
"""


from copy import deepcopy

from win_unc.internal.parsing import drop_while, take_while, first, rfirst, not_
from win_unc.internal.shell import run


class NetUseColumn(object):
    """
    Stores information for a parsing a single column in the output of `NET USE`. This information
    includes the column's name and how to parse it from a row.
    """

    def __init__(self, name, start, end):
        """
        `name` is the column's name.
        `start` is the index in the row that the column's data begins.
        `end` is the index in the row that the column's data ends. If this is `None`, the column
              ends at the end of the row's line.
        """
        self.name = name
        self.start = start
        self.end = end

    def extract(self, string):
        """
        Returns the data for this column from a given row represented by `string`.
        """
        return string[self.start:self.end].strip()

    def __repr__(self):
        return '<{cls} "{name}": {start}-{end}>'.format(
            cls=self.__class__.__name__,
            name=self.name,
            start=self.start,
            end=self.end)


class NetUseTable(object):
    """
    Stores parsed data from the output of `NET USE` and provides easy access methods.
    """

    def __init__(self):
        self.rows = []

    def add_row(self, row):
        """
        Adds `row` to this table. `row` must be a dictionary whose keys are standard column names.
        """
        self.rows.append(row)

    def get_column(self, column):
        """
        Returns a list of all the values in a given `column`.
        """
        return [row[column] for row in self.rows]

    def get_connected_paths(self):
        return self.get_column('remote')

    def get_connected_devices(self):
        return [device for device in self.get_column('local') if device]

    def get_matching_rows(self, local=None, remote=None, status=None):
        """
        Returns a list of rows that match a `search_dict`.
        `search_dict` is a dictionary with a subset of the keys in a row.
        """
        result = []
        for row in self.rows:
            matching = True
            matching &= drive_letters_equal(local, row['local']) if local else True
            matching &= remote_paths_equal(remote, row['remote']) if remote else True
            matching &= status.lower() == row['status'].lower() if status else True

            if matching:
                result.append(row)

        return result



EMPTY_TABLE_INDICATOR = 'There are no entries in the list.'
LAST_TABLE_LINE = 'The command completed successfully.'


# This dictionary maps from the column names in the output of `NET USE` to standardized column
# names that should never change. This allows the output of `NET USE` to change without forcing
# the users of this module to change their code.
MAP_RAW_COLUMNS_TO_STANDARD_COLUMNS = {
    'Local': 'local',
    'Remote': 'remote',
    'Status': 'status',
}


def drive_letters_equal(left, right):
    return left.rstrip(':').lower() == right.rstrip(':').lower()


def normalize_remote_path(path):
    path = path.lower()
    return path[-5:] if path.endswith(r'\ipc$') else path


def remote_paths_equal(left, right):
    return normalize_remote_path(left) == normalize_remote_path(right)


def rekey_dict(d, key_map):
    """
    Renames the keys in `d` based on `key_map`.
    `d` is a dictionary whose keys are a superset of the keys in `key_map`.
    `key_map` is a dictionary whose keys match at least some of the keys in `d` and whose values
              are the new key names for `d`.

    For example:
        rekey_dict({'a': 1, 'b': 2}, {'a': 'b', 'b': 'c'}) =
            {'b': 1, 'c': 2}
    """
    return {new_key: d[old_key]
            for old_key, new_key in key_map.iteritems()}


def is_line_separator(line):
    """
    Returns `True` when `line` is a line separator in a "net use" table.
    """
    return line and all(char == '-' for char in line)


def get_columns(lines):
    """
    Parses the column headers from a "net use" table into a list of `NetUseColumn` objects.
    `lines` is a list of strings from the output of `NET USE`.
    """
    header_iter = take_while(not_(is_line_separator), lines)
    headings = rfirst(lambda x: x and x[0].isalpha(), header_iter)

    names = headings.split()
    starts = [headings.index(name) for name in names]
    ends = [right - 1 for right in starts[1:]] + [None]

    return [NetUseColumn(name, start, end)
            for name, start, end in zip(names, starts, ends)]


def get_body(lines):
    """
    Extracts only the body of the "net use" table. The body is everything between the column
    headers and the end of the output.
    `lines` is a list of strings from the output of `NET USE`.
    """
    bottom = drop_while(not_(is_line_separator), lines)
    is_last_line = lambda x: x and x != LAST_TABLE_LINE
    return (take_while(is_last_line, bottom[1:])
            if len(bottom) > 1
            else [])


def parse_singleline_row(line, columns):
    """
    Parses a single-line row from a "net use" table and returns a dictionary mapping from
    standardized column names to column values.
    `line` must be a single-line row from the output of `NET USE`. While `NET USE` may represent
           a single row on multiple lines, `line` must be a whole row on a single line.
    `columns` must be a list of `NetUseColumn` objects that correctly parses `string`.
    """
    raw_dict = {column.name: column.extract(line) for column in columns}
    return rekey_dict(raw_dict, MAP_RAW_COLUMNS_TO_STANDARD_COLUMNS)


def parse_multiline_row(line1, line2, columns):
    """
    Parses a row from a "net use" table that is represented by two lines instead of just one.
    `line1` is the first line for the row.
    `line2` is the second line for the row.
    `columns` is the unmodified `NetUseColumn` that will correctly parse a single line but not a
              multi-line row.
    """
    singleline_row = line1 + ' ' + line2.strip()
    custom_columns = deepcopy(columns)
    custom_columns[-2].end = len(line1)
    custom_columns[-1].start = len(line1) + 1
    return parse_singleline_row(singleline_row, custom_columns)


def build_net_use_table_from_parts(columns, body_lines):
    """
    Returns a new `NetUseTable` based on `columns` and `body_lines`.
    `columns` is a list of `NetUseColumn` objects.
    `body_lines` is a list of strings representing the raw rows of the table. At times, an actual
                 table row spans multiple lines.
    """
    table = NetUseTable()
    for this_row, next_row in zip(body_lines, body_lines[1:] + ['']):
        if not this_row.startswith(' '):
            if next_row.startswith(' '):
                table.add_row(parse_multiline_row(this_row, next_row, columns))
            else:
                table.add_row(parse_singleline_row(this_row, columns))

    return table


def parse_populated_net_use_table(string):
    """
    Parses a non-empty table from the output of `NET USE` and returns a `NetUseTable`.
    """
    lines = [line.rstrip() for line in string.split('\n')]
    return build_net_use_table_from_parts(get_columns(lines), get_body(lines))


def parse_net_use_table(string):
    """
    Parses `string` into a `NetUseTable` and returns it.
    """
    if EMPTY_TABLE_INDICATOR in string:
        return NetUseTable()
    else:
        return parse_populated_net_use_table(string)
