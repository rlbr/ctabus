from urllib import request
import json
import datetime
import saveto
from timer import timer
bus_timer = timer(t='Bus times',e=True,o=False,a=True)
api = saveto.load('cta_api_key')
def get_times(stop_id,api_key = api):
    url =  "http://www.ctabustracker.com/bustime/api/v2/getpredictions?key={api_key}&stpid={stop_id}&format=json".format(stop_id = stop_id,api_key = api)
    data = json.load(request.urlopen(url))
    times = list(map(lambda time: datetime.datetime.strptime(time['prdtm'],"%Y%m%d %H:%M"),data["bustime-response"]["prd"]))
    return times
walk = datetime.timedelta(seconds = 60*4)
for i in range(6):
    l = get_times(4752)
    print(*map(lambda time: (str(time),str(time-walk)),l),sep = '\n',end = '\n\n')
    try:
        time = next(filter(bool,map(lambda time: time-walk if time-walk > datetime.datetime.today() else False,l)))
        bus_timer(time)
    except:
        print("no times")
