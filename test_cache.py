#!/usr/bin/python
test = False
test = True
from disk_cache import *
@disk_cache
def func(n):
    t = 1
    for i in range(1,n+1):
        t *= i
    return t
if test:
    for i in range(0,10**9,1000):
        print(i)
    func.save_cache()
