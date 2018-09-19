import datetime
from pydoc import pager
def str_coerce(s,**kwargs):
    if isinstance(s,datetime.datetime):
        return s.strftime(kwargs['datetime_format'])
    else:
        return str(s)
def print2d(l,datetime_format = "%A, %B %e, %Y %H:%M:%S",seperator= ' | ',spacer = ' ',bottom = '=',l_end = '|',r_end = '|',interactive = False):
    l = [[str_coerce(s,datetime_format = datetime_format) for s in row] for row in l]
    
    max_col = []
    for row in l:
        for i,col in enumerate(row):
            try:
                max_col[i] = max(max_col[i],len(col))
            except IndexError:
                max_col.append(len(col))
    
    if l_end and r_end:
        fmt_row = f'{l_end} {{content}} {r_end}'
    else:
        fmt_row = '{content}'
    
    done = []
    for row in l:
        content = seperator.join(col.ljust(max_col[i],spacer) for i,col in enumerate(row))
        done.append(fmt_row.format(content = content))
    
    if bottom:
        bottom = bottom*len(done[0])
        row_sep = ('\n'+bottom+'\n')
    else:
        row_sep = '\n'
    final = row_sep.join(done)
    if bottom:
        final = '\n'.join((bottom,final,bottom))
    if interactive:
        pager(final)
    else:
        return final