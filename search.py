from editdistance import eval as editdistance
import re
import json
class StopSearch:
    def __init__(self,query):
        parts = re.split(r' ?(?:and|&) ?',query)
        self.query = ' & '.join(parts)
        self.query_reversed = ' & '.join(reversed(parts))
    def __call__(self,stop):
        stop = stop.lower()
        return min(
            editdistance(self.query,stop),
            editdistance(self.query_reversed,stop)
            )
    def __str__(self):
        return '{}|{}'.format(self.query,self.query_reversed)
    def __repr__(self):
        return str(self)
if __name__ == "__main__":
    with open('stops_out.json') as file:
        data = json.load(file)
        names = [stop['stpnm'] for stop in data['stops']]