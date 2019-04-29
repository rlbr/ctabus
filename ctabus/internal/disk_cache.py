import lzma
import os
import pickle
import atexit

from ctabus.internal.config import cache_dir


def make_key(*args, **kwargs):

    return args, tuple(sorted(
        kwargs.items(), key=lambda item: item[0]))


class disk_cache:
    """Decorator to make persistent cache"""
    caches = []
    use_lzma = True

    def __init__(self, func):
        if disk_cache.use_lzma:
            self.fname = "{}.{}.dc.lzma".format(func.__module__, func.__name__)
        else:
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
            if disk_cache.use_lzma:
                with lzma.open(self.fname, 'rb') as file:
                    cache = pickle.load(file)
            else:
                with open(self.fname, 'rb') as file:
                    cache = pickle.load(file)
            self.fresh = False
        except FileNotFoundError:
            cache = {}
            self.fresh = True
        self.cache = cache

    def save_cache(self):
        if disk_cache.use_lzma:
            with lzma.open(self.fname, 'wb') as file:
                pickle.dump(self.cache, file, pickle.HIGHEST_PROTOCOL)
        else:
            with open(self.fname, 'wb') as file:
                pickle.dump(self.cache, file, pickle.HIGHEST_PROTOCOL)

    def delete_cache(self):
        os.remove(self.fname)
        self.cache = {}
        self.fresh = True


def save_if_modified():
    for cache_obj in disk_cache.caches:
        if cache_obj.fresh:
            cache_obj.save_cache()


atexit.register(save_if_modified)
