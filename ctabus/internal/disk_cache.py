import lzma
import os
import pickle

from ctabus.internal.config import cache_dir


def make_key(*args, **kwargs):

    return args, tuple(sorted(
        kwargs.items(), key=lambda item: item[0]))


class disk_cache:
    """Decorator to make persistent cache"""
    caches = []

    def __init__(self, func):
        self.fname = "{}.{}.dc".format(func.__module__, func.__name__)
        self.fname = os.path.join(cache_dir, self.fname)
        self.func = func
        self.load_cache()
        disk_cache.caches.append(self)

    def __call__(self, *args, **kwargs):
        key = make_key(*args, **kwargs)
        try:
            res = self.cache[key]
            return res
        except KeyError:
            self.fresh = True
            res = self.func(*args, **kwargs)
            self.cache[key] = res
            return res

    def load_cache(self):
        try:
            with lzma.open(self.fname, 'rb') as file:
                cache = pickle.load(file)
                self.fresh = False
        except FileNotFoundError:
            cache = {}
            self.fresh = True
        self.cache = cache

    def save_cache(self):
        with lzma.open(self.fname, 'wb') as file:
            pickle.dump(self.cache, file, pickle.HIGHEST_PROTOCOL)

    def delete_cache(self):
        os.remove(self.fname)
        self.cache = {}
        self.fresh = True
