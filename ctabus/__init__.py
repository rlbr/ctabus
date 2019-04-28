#!/usr/bin/python3
from dateutil.parser import parse as date_parse
from dateutil import tz
import argparse
import datetime
import os
import re
import socket
import time
import urllib
import subprocess
import os.path as osp
import sys
import shutil

from ctabus.internal.config import log_dir
from ctabus.internal.disk_cache import disk_cache, make_key
from ctabus import fetch

HAS_TOAST = shutil.which('termux-toast') is not None
CHICAGO_TZ = tz.gettz("America/Chicago")
DATETIME_FORMAT = "%A, %B %e, %Y %H:%M:%S"
# https://stackoverflow.com/a/5967539

parser = argparse.ArgumentParser(prog='ctabus')
parser.add_argument('-l', '--lucky', action='store_true',
                    help='picks first result')
parser.add_argument('-p', '--periodic', metavar='SEC',
                    type=int, help='checks periodically')
parser.add_argument('-r', '--route', default=None)
parser.add_argument('-d', '--direction', default=None)
parser.add_argument('-t', '--disable_toast', action='store_false')
parser.add_argument('-k', '--kill-cache', action="store_true")
parser.add_argument('arg', nargs='+', metavar='(stop-id | cross streets)')


def toast(text):
    read, write = os.pipe()
    os.write(write, text.encode())
    os.close(write)
    subprocess.Popen(["termux-toast", "-g", "top", "-c", "white", "-b", "black"],
                     stdin=read)


def atoi(text):
    return int(text) if text.isdigit() else text


def numb_sort(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def clearscr():
    os.system('cls' if os.name == 'nt' else 'clear')


def pprint_delta(delta):
    delta = str(delta)
    days = None
    s1 = delta.split(', ')
    if len(s1) > 1:
        days, time = s1
    else:
        time = s1[0]
    time = time.split('.')[0]
    hour, minute, second = map(int, time.split(':'))
    time = ''
    if hour:
        time += '{hour} hour'.format(hour=hour) + ('s' if hour != 1 else '')
    if minute:
        if time and not time.endswith(', '):
            time += ', '
        time += '{minute} minute'.format(minute=minute) + \
            ('s' if minute != 1 else '')
    if second:
        if time and not time.endswith(', '):
            time += ', '
        time += '{second} second'.format(second=second) + \
            ('s' if second != 1 else '')
    ret = ''
    if days:
        ret = days + ', ' if time else ''
    ret += time
    return ret


def gen_list(objs, data, *displays, key=None, sort=0, num_pic=True):
    from ctabus.internal.print2d import create_table, render_table
    # sort based on column number
    k = displays[sort]
    display_data = {obj[k]: obj[data] for obj in objs}
    srt_keys = sorted(display_data.keys(), key=key)

    display = sorted(
        [
            [obj[d] for d in displays] for obj in objs
        ],
        key=lambda row: key(row[sort]) if key else row[sort]
    )
    if num_pic:
        display = [[i] + data for i, data in enumerate(display)]

    table = create_table(display, DATETIME_FORMAT)
    render_table(table)
    if num_pic:
        which = None
        while not which:
            try:
                which = input('Which one?: ')
            except KeyboardInterrupt:
                quit()
            try:
                which = srt_keys[int(which)]
            except (ValueError, IndexError):
                which = None
        return display_data[which]
    else:
        ret = None
        while not ret:
            try:
                ret = display_data[input('Which one?: ')]
            except KeyError:
                pass
        return ret


config = '''\
{route} - {end} ({direction})
{nm}, stop {stop_id}
{delta} ({t})\
'''


def show(data, rt_filter=None, _clear=False, enable_toast=False):
    times = data['prd']
    now = datetime.datetime.now(CHICAGO_TZ)
    arrivals = sorted(times, key=lambda t: t['prdtm'])
    if rt_filter is not None:
        arrivals = filter(lambda arrival: arrival['rt'] == rt_filter, arrivals)
    if _clear:
        clearscr()
    do_toast = True
    for bustime in arrivals:
        before = date_parse(bustime['prdtm'])
        arrival = before.replace(tzinfo=CHICAGO_TZ)
        if arrival > now:
            stop_id = bustime['stpid']
            delta = pprint_delta(arrival-now)
            t = arrival.strftime('%H:%M:%S')
            route = bustime['rt']
            direction = bustime['rtdir']
            end = bustime['des']
            nm = bustime['stpnm'].rstrip()
            if do_toast and enable_toast:
                toast(config.format(**locals()) + '\n'*2+"\n")
                do_toast = False
            print(
                config.format(**locals()), end='\n'*2
            )
    print("="*36)


def _picker(args):
    # save on import time slightly
    from ctabus.internal.search import Search, StopSearch
    # routes
    if not args.route:
        data = fetch.get_routes()['routes']
        route = gen_list(data, 'rt', 'rt', 'rtnm',
                         num_pic=False, key=numb_sort)
    else:
        route = args.route
    data = fetch.get_directions(route)['directions']
    # direction
    if not args.direction:
        for direction_obj in data:
            friendly_name = fetch.get_name_from_direction(
                route, direction_obj['dir'])
            direction_obj['friendly_name'] = friendly_name
        direction = gen_list(data, 'dir', 'dir', 'friendly_name')
    else:
        s = Search(args.direction)
        direction = sorted((obj['dir'] for obj in data), key=s)[0]
    # direction
    stops = fetch.get_stops(route, direction)['stops']
    s = StopSearch(args.arg)
    if args.lucky:
        stop_id = sorted(stops, key=lambda stop: s(stop['stpnm']))[
            0]['stpid']
    else:
        stop_id = gen_list(stops, 'stpid', 'stpnm', key=s)
    return stop_id


def _picker_recent(args):
    pass


def _main_periodic(args, stop_id, init_data):
    _done = False
    data = init_data
    while not _done:
        try:
            try:
                show(data, args.route, True, args.disable_toast and HAS_TOAST)
                s = time.perf_counter()
                timeout = 1
                if args.periodic > timeout:
                    timeout = args.periodic
                data = fetch.get_times(stop_id, timeout=timeout)
                e = time.perf_counter() - s
            except (urllib.error.URLError, socket.timeout):
                e = time.perf_counter() - s
                print("Error fetching times")
            if e < args.periodic:
                time.sleep(args.periodic-e)
        except KeyboardInterrupt:
            _done = True


def main(args=None):
    if args is None:
        args = parser.parse_args()
    sys.stderr = open(osp.join(log_dir, 'stderr.log'), 'w')
    if args.kill_cache:
        for cache_obj in disk_cache.caches:
            cache_obj.delete_cache()
    args.arg = ' '.join(args.arg)

    if args.arg.isdecimal():
        stop_id = args.arg
    else:
        if args.arg == ':recent:':
            pass
        else:
            stop_id = _picker(args)

    data = fetch.get_times(stop_id)
    info = data['prd'][0]
    key = make_key(info['rt'], info['rtdir'], fetch.api, None)
    if key not in fetch.get_name_from_direction.cache.keys():
        fetch.get_name_from_direction.cache[key] = info['des']
        fetch.get_name_from_direction.fresh = True

    if args.periodic is not None:
        _main_periodic(args, stop_id, data)
    else:
        show(data, args.route)
    for cache_obj in disk_cache.caches:
        if cache_obj.fresh:
            cache_obj.save_cache()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)