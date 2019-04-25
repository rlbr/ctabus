import re
import json

import edlib


def editdistance(a, b):
    return edlib.align(a, b)['editDistance']


class Search:
    def __init__(self, query):
        self.raw_lower = query.lower()

    def __call__(self, arg):
        arg = arg.lower()
        return editdistance(self.raw_lower, arg)

    def __str__(self):
        print(self.raw_lower)

    def __repr__(self):
        return str(self)


class StopSearch(Search):
    def __init__(self, query):
        super().__init__(query)
        query = query.lower()
        parts = re.split(r' ?(?:(?<!\w)and(?!\w)|&) ?', query)
        self.query = ' & '.join(parts)
        self.query_reversed = ' & '.join(reversed(parts))

    def __call__(self, stop):
        stop = stop.lower()
        paren = re.search(r'\((?P<data>[^\)]+)\)', stop)
        ret = [
            editdistance(self.query, stop),
            editdistance(self.query_reversed, stop),
        ]
        if paren:
            paren = paren.group('data')
            ret.append(editdistance(self.query, paren))
        if self.raw_lower in stop:
            ret = (item - 100 for item in ret)
        return min(
            ret
        )

    def __str__(self):
        return '{}|{}'.format(self.query, self.query_reversed)


if __name__ == "__main__":
    with open('stops_out.json') as file:
        data = json.load(file)
        names = [stop['stpnm'] for stop in data['stops']]
    while True:
        q = StopSearch(input('Search: '))
        print('\n'.join(sorted(names, key=q)), end='\n'*3)
