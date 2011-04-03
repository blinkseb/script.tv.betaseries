# -*- coding: utf-8 -*-

import pprint

class TVShow:
    __id = 0
    __name = ""
    def __init__(self, id):
        self.__id = id

    def id(self):
        return self.__id

class XBMCLib:
    __tvShows = {}
    
    def __init__(self, socket):
        self.socket = socket
        self.requestLibrary()

    def requestLibrary(self):
        request = {}
        request['id'] = self.socket.getId()
        request['method'] = "VideoLibrary.GetTVShows"
        request['params'] = {}
        request['params']['fields'] = ['plot', 'title']
        self.socket.addCallbackForId(self.socket.getId(), self.callback)
        self.socket.send(request);

    def callback(self, data):
        if data.action == "VideoLibrary.GetTVShows":
            id = int(data.data['result']['tvshows'][0]['tvshowid'])
            self.__tvShows[self.socket.getId()] = TVShow(id)
            self.__tvShows[self.socket.getId()].__name = data.data['result']['tvshows'][0]['title']
            request = {}
            request['id'] = self.socket.getId()
            self.socket.addCallbackForId(self.socket.getId(), self.callback)
            request['method'] = "VideoLibrary.GetSeasons"
            request['params'] = {}
            request['params']['fields'] = ['plot', 'title', 'season']
            request['params']['tvshowid'] = id
            self.socket.send(request)
        elif data.action == "VideoLibrary.GetSeasons":
            request = {}
            request['id'] = self.socket.getId()
            self.socket.addCallbackForId(self.socket.getId(), self.callback)
            request['method'] = "VideoLibrary.GetEpisodes"
            request['params'] = {}
            request['params']['tvshowid'] = self.__tvShows[int(data.data['id'])].id()
            request['params']['fields'] = ['plot', 'title']
            request['params']['season'] = data.data['result']['seasons'][0]['season']
            self.socket.send(request)
        elif data.action == "VideoLibrary.GetEpisodes":
            
        return True
