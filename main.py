# from argparse import parser
from print2d import print2d
import re
# parser = argparse.ArgumentParser(prog = 'ctabus')
# parser.add_argument('arg',metavar = 'stop-id | cross streets')
# parser.add_argument('-r','--route',default = None)
# parser.add_argument('-d','--direction',default = None)
# args = parser.parse_args()
def numb_sort(str):
    n = 40
    try:
        return re.sub(r'\d+',lambda match: match.group(0).rjust(n,'0'),str)
    except Exception as E:
        print(str)
        raise E
    
def gen_list(objs,data,*displays,key = None,sort = 0,num_pic = True):
    k = displays[sort]
    display_data = {obj[k]:obj[data] for obj in objs}
    srt_keys = sorted(display_data.keys(),key=key)

    display = sorted(
        [
            [obj[d] for d in displays] for obj in objs
        ],
        key = lambda row: key(row[sort])
    )
    if num_pic:
        display = [[i] + data for i,data in enumerate(display)]
    
    opts = {
        'spacer':' ',
        'seperator':' ',
        'interactive': True,
        'bottom':'=',
        'l_end':'<',
        'r_end':'>',
        }
    print2d(display,**opts)
    if num_pic:
        which = None
        while not which:
            try:
                which = srt_keys[int(input('Which one?: '))]
            except ValueError:
                which = None
        return display_data[which]
    else:
        ret = None
        while not ret:
            try:
                ret =  display_data[input('Which one?: ')]
            except KeyError:
                pass
        return ret
        

if __name__ == "__main__":
    import json
    with open('stops_out.json') as file:
        d= json.load(file)

    d = d['stops']
    print(gen_list(d,'stpid','stpnm',key=numb_sort,num_pic=True))
