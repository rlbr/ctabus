import os

import appdirs

app_dirs = appdirs.AppDirs('ctabus')
config_dir = app_dirs.user_config_dir
cache_dir = app_dirs.user_cache_dir
log_dir = app_dirs.user_log_dir
for dir in (config_dir, cache_dir, log_dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
try:
    with open(os.path.join(config_dir, 'api.txt')) as file:
        API_KEY = file.read().rstrip()
except FileNotFoundError:
    raise FileNotFoundError("Please place your CTA Bus Tracker api key in a text file located at '{}'".format(
        os.path.join(config_dir, 'api.txt')))
