#-*-coding:utf-8-*-

APP_KEY = ''
APP_SECRET = ''

WEB_SERVER_HOST = ''
REDIRECT_URL = WEB_SERVER_HOST + '/'

SERVER_HOST = ''
SERVER_IPv6 = False
SERVER_PORT = 1024

try:
    from local_config import *
except:
    pass
