from urllib.parse import urlencode
from requests import get
import json
import datetime
test = False
test = True
with open('cta_api_key') as file:
    api = file.read()

def get_data(type,api_key = api,**args):
    base_url = "http://www.ctabustracker.com/bustime/api/v2/{type}?{query}"
    args['key'] = api_key
    args['format'] = 'json'
    url = base_url.format(type = type,query = urlencode(args))
    print(url)
    input()
    response = get(url)
    data = json.loads(response.text)
    return data['bustime-response']
    # print(url)
    
def print2d(values):
	pass
def get_times(stop_id,api_key = api):
    return get_data('getpredictions',api_key,stpid=stop_id)
    
def get_routes(api_key = api):
    return get_data('getroutes',api_key)
    
def get_directions(route,api_key = api):
    return get_data('getdirections',api_key,rt=route)
    
def get_stops(route,direction,api_key = api):
    return get_data('getstops',api_key,rt = route,dir=direction)

