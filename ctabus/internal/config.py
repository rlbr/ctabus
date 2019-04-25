import os

import appdirs

app_dirs = appdirs.AppDirs('ctabus')
config_dir = app_dirs.user_config_dir
cache_path = app_dirs.user_cache_dir
try:
    with open(os.path.join(config_dir, 'api.txt')) as file:
        API_KEY = file.read().rstrip()
except FileNotFoundError:
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    raise FileNotFoundError("Please place your CTA Bus Tracker api key in a text file located at '{}'".format(
        os.path.join(config_dir, 'api.txt')))
