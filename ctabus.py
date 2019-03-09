from urllib.parse import urlencode
from urllib.request import urlopen
import json
from sensitive import api


def get_data(type, api_key=api, timeout=None, **args):
    base_url = "http://www.ctabustracker.com/bustime/api/v2/{type}?{query}"
    args['key'] = api_key
    args['format'] = 'json'
    url = base_url.format(type=type, query=urlencode(args))
    if timeout is not None:
        response = urlopen(url,timeout = timeout)
    else:
        response = urlopen(url)
    data = json.load(response)['bustime-response']
    try:
        data['error']
        raise Exception(str(data["error"]))
    except KeyError:
        return data


def get_times(stop_id, api_key=api, timeout=None):
    return get_data('getpredictions', api_key, stpid=stop_id, timeout=timeout)


def get_routes(api_key=api, timeout=None):
    return get_data('getroutes', api_key, timeout=timeout)


def get_directions(route, api_key=api, timeout=None):
    return get_data('getdirections', api_key, rt=route, timeout=timeout)


def get_stops(route, direction, api_key=api, timeout=None):
    return get_data('getstops', api_key, rt=route, dir=direction, timeout=timeout)
