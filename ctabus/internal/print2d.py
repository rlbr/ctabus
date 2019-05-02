import datetime
import os
import sys
from pydoc import pipepager, tempfilepager, plainpager, plain

from terminaltables import AsciiTable
from terminaltables.terminal_io import terminal_size
from textwrap import fill


def getpager():
    """Decide what method to use for paging through text."""
    if not hasattr(sys.stdin, "isatty"):
        return plainpager
    if not hasattr(sys.stdout, "isatty"):
        return plainpager
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return plainpager
    use_pager = os.environ.get('MANPAGER') or os.environ.get('PAGER')
    if use_pager:
        if sys.platform == 'win32':  # pipes completely broken in Windows
            return lambda text: tempfilepager(plain(text), use_pager)
        elif os.environ.get('TERM') in ('dumb', 'emacs'):
            return lambda text: pipepager(plain(text), use_pager)
        else:
            return lambda text: pipepager(text, use_pager)
    if os.environ.get('TERM') in ('dumb', 'emacs'):
        return plainpager
    if sys.platform == 'win32':
        return lambda text: tempfilepager(plain(text), 'more <')
    if hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        return lambda text: pipepager(text, 'less -X')


def str_coerce(s, **kwargs):
    if isinstance(s, datetime.datetime):
        return s.strftime(kwargs['datetime_format'])
    else:
        return str(s)


def create_table(list_param, datetime_format):
    rows = []
    for row in list_param:
        rows.append([])
        for item in row:
            rows[-1].append(str_coerce(item, datetime_format=datetime_format))
    return AsciiTable(rows)


def fix_iteration(table: AsciiTable, max_width):
    col_length = len(table.table_data[0])
    average_size = ((max_width-1) // col_length)
    average_size = average_size - \
        (1 + table.padding_left + table.padding_right)
    sizes = list(map(lambda init_size: 1 + table.padding_left +
                     init_size + table.padding_right, table.column_widths))
    # pick the biggest column to work on
    sorted_sizes = sorted(
        range(col_length), key=lambda i: sizes[i], reverse=True)
    workon = sorted_sizes[0]
    # either do the maximum possible size or the average size, which ever is larger. The other rows will accommodate.
    wrap_to = max(
        (
            average_size,
            (max_width-1) - table.table_width +
            table.column_widths[workon]
        )
    )
    if wrap_to > 0:
        for row in table.table_data:
            row[workon] = fill(row[workon], wrap_to+1)
        return True
    else:
        return False


def render_table(table: AsciiTable, interactive=True):
    '''Do all wrapping to make the table fit in screen'''
    MAX_WIDTH = terminal_size()[0]
    table.inner_row_border = True
    if not table.table_width < MAX_WIDTH:
        non_negative = True
        i = 0
        while table.table_width > MAX_WIDTH and non_negative and i < 50:
            non_negative = fix_iteration(table, MAX_WIDTH)
            i += 1

    if interactive:
        pager = getpager()
        pager(table.table)
    else:
        print(table.table)
