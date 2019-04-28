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


def render_table(table: AsciiTable, interactive=True):
    '''Do all wrapping to make the table fit in screen'''
    table.inner_row_border = True
    data = table.table_data
    terminal_width = terminal_size()[0]
    n_cols = len(data[0])
    even_distribution = terminal_width // n_cols
    for row_num, row in enumerate(data):
        for col_num, col_data in enumerate(row):
            if len(col_data) > even_distribution:
                if col_num != n_cols - 1:
                    data[row_num][col_num] = fill(col_data, even_distribution)
                else:
                    data[row_num][col_num] = ''
                    data[row_num][col_num] = fill(
                        col_data, table.column_max_width(col_num))
    if interactive:
        pager = getpager()
        pager(table.table)
    else:
        print(table.table)
