import pickle
import os
import lmza
cache_path = os.path.abspath(os.path.join(__file__, "..", "__pycache__"))
if not os.path.exists(cache_path):
    os.mkdir(cache_path)


class disk_cache:
    def __init__(self, func):
        self.fname = "{}.{}.dc".format(func.__module__, func.__name__)
        fname = os.path.join(cache_path, fname)
        self.func = func
        self.cache = self.load_cache()

    def call(self, *args, **kwargs):
        key = args + tuple(sorted(self.kwargs.items(), key=lambda item))
        try:
            return self.cache[key]
        except KeyError:
            res = self.func(*args, **kwargs)
            self.cache[key] = res

    def load_cache(self):
        try:
            with lmza.open(self.fname, 'rb') as file:
                cache = pickle.load(file)
        except FileNotFoundError:
            cache = {}
        self.cache = cache

    def save_cache(self):
        with lmza.open(self.fname, 'wb') as file:
            pickle.dump(self.cache, file)
