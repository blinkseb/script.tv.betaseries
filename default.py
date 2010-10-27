# -*- coding: utf-8 -*-

__script__       = "BetaSeries.com"
__addonID__      = "script.tv.betaseries"
__author__       = "blinkseb"
__url__          = "http://github.com/blinkseb/script.tv.betaseries"
__svn_url__      = "http://github.com/blinkseb/script.tv.betaseries"
__credits__      = "blinkseb"
__platform__     = "xbmc media center, [ALL]"
__date__         = "25-10-2010"
__version__      = "0.1"
__useragent__    = "BetaSeries.com XBMC addon"

__betaseries_url__ = "http://api.betaseries.com/"
__key__            = "ed768c9dc6d3"

from socket import *
import json
import urllib2
import socket
import sys

def formatUrl(url, params=None):
    base = __betaseries_url__ + url + ".json?key=" + __key__
    if params is None:
        return base
    else:
        lst = ""
        for (key, value) in params.items():
            lst += "&" + str(key) + "=" + str(value)
        return base + lst
        
def loadUrl(url):
    request = urllib2.Request(url)
    print "trying to load url: " + request.get_full_url()
    opener = urllib2.build_opener()
    request.add_header('User-Agent', __useragent__) 
    return opener.open(request).read()

port = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", port))

postdata = '{"jsonrpc": "2.0", "method": "JSONRPC.Version", "id": "1"}'
s.send(postdata)
respdata = json.read(s.recv(4096))
jsonrpc_version = respdata["result"]["version"]

postdata = '{"jsonrpc": "2.0", "method": "JSONRPC.SetAnnouncementFlags", "params": {"playback": 1}, "id": "1"}'
s.send(postdata)
s.recv(4096)

postdata = '{"jsonrpc": "2.0", "method": "JSONRPC.SetAnnouncementFlags", "params": {"gui": 1}, "id": "1"}'
s.send(postdata)
s.recv(4096)

while (1):
    data = s.recv(4096)
    print "got new json data: " + data
    
    js = json.read(data)
    if "method" in js:
        if (js["method"] == "Announcement") and (js["params"]["sender"] == "xbmc"):
            if (js["params"]["message"] == "ApplicationStop"):
                break
                

s.close();