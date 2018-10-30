import argparse
import re
import ctabus
from dateutil.parser import parse as date_parse
import datetime
# for logging
import sys
import os.path as osp
def numb_sort(str):
    n = 40
    try:
        return re.sub(r'\d+',lambda match: match.group(0).rjust(n,'0'),str)
    except Exception as E:
        print(str)
        raise E

def pprint_delta(delta):
    delta = str(delta)
    days= None
    s1 = delta.split(', ')
    if len(s1) > 1:
        days,time = s1
    else:
        time = s1[0]
    time = time.split('.')[0]
    hour,minute,second = map(int,time.split(':'))
    time = ''
    if hour:
        time += f'{hour} hour' + ('s' if hour != 1 else '')
    if minute:
        if time and not time.endswith(', '):
            time += ', '
        time += f'{minute} minute' + ('s' if minute != 1 else '')
    if second:
        if time and not time.endswith(', '):
            time += ', '
        time += f'{second} second' + ('s' if second != 1 else '')
    ret = ''
    if days:
        ret = days + ', ' if time else ''
    ret += time
    return ret

def gen_list(objs,data,*displays,key = None,sort = 0,num_pic = True):
    k = displays[sort]
    display_data = {obj[k]:obj[data] for obj in objs}
    srt_keys = sorted(display_data.keys(),key=key)

    display = sorted(
        [
            [obj[d] for d in displays] for obj in objs
        ],
        key = lambda row: key(row[sort]) if key else row[sort]
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
                which = input('Which one?: ')
            except KeyboardInterrupt:
                quit()
            try:
                which = srt_keys[int(which)]
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

config = '''\
{route} - {end} ({direction})
{nm}, stop {stop_id}
{delta} ({t})\
'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'ctabus')
    parser.add_argument('arg',nargs = '+',metavar = '(stop-id | cross streets)')
    parser.add_argument('-r','--route',default = None)
    parser.add_argument('-d','--direction',default = None)
    parser.add_argument('-l','--lucky',action='store_true',help = 'picks first result')
    args = parser.parse_args()
    sys.stderr = open(osp.join(osp.dirname(__file__),'stderr.log'),'w')
    args.arg = ' '.join(args.arg)

    if not args.arg.isdecimal():
        # save on import time slightly
        from print2d import print2d
        from search import Search,StopSearch
        #routes
        if not args.route:
            data = ctabus.get_routes()['routes']
            route = gen_list(data,'rt','rt','rtnm',num_pic = False,key=numb_sort)
        else:
            route = args.route
        data = ctabus.get_directions(route)['directions']
        #direction
        if not args.direction:
            direction = gen_list(data,'dir','dir')
        else:
            s = Search(args.direction)
            direction = sorted((obj['dir'] for obj in data),key = s)[0]
        #direction
        stops = ctabus.get_stops(route,direction)['stops']
        s = StopSearch(args.arg)
        if args.lucky:
            stop_id = sorted(stops,key=lambda stop: s(stop['stpnm']))[0]['stpid']
        else:
            stop_id = gen_list(stops,'stpid','stpnm',key = s)
    else:
        stop_id = args.arg
    times = ctabus.get_times(stop_id)['prd']
    today = datetime.datetime.today()
    for time in sorted(times,key = lambda t: t["prdtm"]):
        arrival = date_parse(time['prdtm'])
        if arrival > today:
            delta = pprint_delta(arrival-today)
            t = arrival.strftime('%H:%M:%S')
            route = time['rt']
            direction = time['rtdir']
            end = time['des']
            nm = time['stpnm']
            print(
                config.format(**globals()),end= '\n'*2
            )
