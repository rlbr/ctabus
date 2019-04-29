import atexit
import json
import os

import appdirs

app_dirs = appdirs.AppDirs('ctabus')
config_dir = app_dirs.user_config_dir
cache_dir = app_dirs.user_cache_dir
log_dir = app_dirs.user_log_dir
state_dir = app_dirs.user_state_dir

for dir in (config_dir, cache_dir, log_dir, state_dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

recent_json = os.path.join(state_dir, "recent.json")
try:
    with open(os.path.join(config_dir, 'api.txt')) as file:
        API_KEY = file.read().rstrip()
except FileNotFoundError:
    raise FileNotFoundError("Please place your CTA Bus Tracker api key in a text file located at '{}'".format(
        os.path.join(config_dir, 'api.txt')))


class RecentList:
    def __init__(self, maxsize=10):
        self.maxsize = maxsize
        try:
            with open(recent_json) as file:
                self.elements = json.load(file)
            self.fresh = False
        except FileNotFoundError:
            self.elements = []
            self.fresh = True

    def add(self, element):
        if len(self.elements)+1 > self.maxsize:
            del self.elements[-1]
        self.elements.insert(0, element)
        self.fresh = True

    def get(self, element_name_or_index):
        if type(element_name_or_index) == int:
            index = element_name_or_index
        else:
            index = self.elements.index(element)
        ret = self.elements.pop(index)
        self.elements.insert(0, ret)
        self.fresh = True
        return ret

    def save(self):
        if self.fresh:
            with open(recent_json, 'w') as file:
                json.dump(self.elements, file, sort_keys=True, indent=4)


recent_list = RecentList()


def save_if_modified():
    if recent_list.fresh:
        recent_list.save()


atexit.register(save_if_modified)
