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

import json
import urllib2
import sys
import md5
from mySocket import BSSocket
from XBMCLibrary import XBMCLib

import pprint
import difflib

username = "xbmc"
password = "5a1bc0ed8b9a102fe8754226f62e6c1f"
__token__ = None

def formatUrl(url, params=None):
    base = __betaseries_url__ + url + ".json?key=" + __key__
    if not (__token__ is None):
      base += "&token=" + __token__
      
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
    
def logUser():
    global __token__
    data = json.read(loadUrl(formatUrl("members/auth", {"login": username, "password": password})))
    if (data["root"]["code"] == 1):
        __token__ = data["root"]["member"]["token"]
        print "Successfully logged in"
    else:
      print "Failed to login. Check your login/pwd"
      
def unlogUser():
    global __token__
    loadUrl(formatUrl("members/destroy"))
    __token__ = None
    
def getBSTVShowName(name):
    print "trying to get BetaSeries tvshow name for %s" % name
    js = json.read(loadUrl(formatUrl("shows/search", {"title": name})))
    shownames = {}    
    for (key, value) in js["root"]["shows"].items():
      shownames[ value["title"] ] = value["url"]
      
    res = difflib.get_close_matches(name, shownames.keys(), 1)
    if res:
      print "Closest show name: %s with url: %s" % (res[0], shownames[res[0]])
      return shownames[res[0]]
      
    return ""

def formatJSON(method, id, params):
    request = {}
    request["jsonrpc"] = "2.0"
    request["id"] = id
    request["method"] = method
    request["params"] = params
    return json.write(request)
    
def getVideoDetails(content, id, _fields = []):
    global global_id
    global s
    fields = []
    if (not _fields):
      fields = ["title"]
    else:
      fields = _fields
      
    method = "VideoLibrary.Get"
    if (content == "tvshow"):
      method += "TVShowDetails"
    elif (content == "episode"):
      method += "EpisodeDetails"
    elif (content == "movie"):
      method += "MovieDetails"
    elif (content == "musicvideo"):
      method += "MusicVideoDetails"
    
    params = {}
    params["fields"] = fields;
    params[content + "id"] = id;
      
    request = formatJSON(method, global_id, params)
    global_id += 1;
    s.send(request)
    
def processNewTVShow(details):
    print "We have a new TVShow: %s" % details["title"]
    showname = getBSTVShowName(details["title"])
    data = json.read(loadUrl(formatUrl("shows/add/" + showname)))
    if (data["root"]["code"] != 1):
      print "Failed to add new tv show to betaserie. Error code %s" % data["root"]["code"]
    

socket = BSSocket()
socket.connect()
lib = XBMCLib(socket)

#logUser()

while (1):
    
    data = socket.get()

    print "[MAIN] action: " + data.action
    
##    js = data.data
##    
##    if "method" in js:
##        if (js["method"] == "Announcement") and (js["params"]["sender"] == "xbmc"):
##            msg = js["params"]["message"]
##            data = None
##            if "data" in js["params"]:
##                data = js["params"]["data"]
##                
##            if (msg == "UpdateVideo") and (data != None):
##                content = None
##                id = None
##                if ("content" in data):
##                  content = data["content"]
##                
##                if (content != None):
##                  strId = content + "id"
##                  if (strId in data):
##                    id = data[strId]
##                
##                if (content == "tvshow"):
##                  id_action[str(global_id)] = "add_tvshow"
##                  getVideoDetails(content, id)
##                  
##            if (msg == "RemoveVideo") and (data != None):
##                content = None
##                id = None
##                if ("content" in data):
##                  content = data["content"]
##                
##                if (content != None):
##                  strId = content + "id"
##                  if (strId in data):
##                    id = data[strId]
##                
##                if (content == "tvshow"):
##                  id_action[str(global_id)] = "remove_tvshow"
##                  getVideoDetails(content, id)
##                  
##            if (msg == "ApplicationStop"):
##                break
##                
##    if "result" in js:
##        if ("tvshowdetails" in js["result"]):
##          id = str(js["id"])
##          if (id in id_action):
##            print "Found action for id %s: %s" % (id, id_action[id])
##            if (id_action[id] == "add_tvshow"):
##              processNewTVShow(js["result"]["tvshowdetails"][0])
##            elif (id_action[id] == "remove_tvshow"):
##              print ""

socket.close();
#unlogUser()
