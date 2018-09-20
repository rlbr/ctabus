from editdistance import eval as editdistance
import re
import json
class StopSearch:
    def __init__(self,query):
        query = query.lower()
        parts = re.split(r' ?(?:(?<!\w)and(?!\w)|&) ?',query)
        self.query = ' & '.join(parts)
        self.query_reversed = ' & '.join(reversed(parts))
    def __call__(self,stop):
        stop = stop.lower()
        paren = re.search(r'\((?P<data>[^\)]+)\)',stop)
        ret= [
            editdistance(self.query,stop),
            editdistance(self.query_reversed,stop),
        ]
        if paren:
            paren = paren.group('data')
            ret.append(editdistance(self.query,paren))
        return min(
                ret
            )
    def __str__(self):
        return '{}|{}'.format(self.query,self.query_reversed)
    def __repr__(self):
        return str(self)
if __name__ == "__main__":
    with open('stops_out.json') as file:
        data = json.load(file)
        names = [stop['stpnm'] for stop in data['stops']]
    while True:
        q = StopSearch(input('Search: '))
        print('\n'.join(sorted(names,key=q)))