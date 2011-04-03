import socket
import threading
import Queue
import json
import time

class BSSocketData:
  pass

class BSSocketReader(threading.Thread):
  def __init__(self, socket):
    self.socket = socket
    self.q = Queue.Queue()
    self.__stopevent = threading.Event( )
    threading.Thread.__init__ ( self )
    
  def run(self):
    while not self.__stopevent.isSet():
      _data = self.socket.socket.recv(4096)
      if len(_data) == 4096:
        self.socket.socket.setblocking(0)
        while(1):
          try:
            buf = self.socket.socket.recv(4096)
            _data += buf
            if len(buf) == 4096:
              continue
          except socket.error:
            self.socket.socket.setblocking(1)
            break
      print "got new json data: " + _data

      if len(_data) == 0:
        break
      
      js = json.read(_data)
      if "id" in js:
        action = self.socket.getActionForId(js['id'])
      else:
        action = "ANNOUNCEMENTS"

      socketData = BSSocketData()
      socketData.action = action
      socketData.data = js
      if ("id" in js):
        if not self.socket.notifyId(int(js['id']), socketData):
          self.q.put(socketData)
      else:
        self.q.put(socketData)

  def stop(self):
    self.__stopevent.set()

  def get(self):
    return self.q.get(True)

class BSSocket:
  __port = 9090
  __map = {1: "VERSION", 2: "PERMISSIONS"}
  __id = 3
  __callbacks = {}
  
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pass
  
  def connect(self):
    self.socket.connect(("localhost", self.__port))
    self.__thread = BSSocketReader(self)
    self.__thread.start()

    self.socket.send('{"jsonrpc": "2.0", "method": "JSONRPC.Version", "id": "1"}')
    self.socket.send('{"jsonrpc": "2.0", "method": "JSONRPC.SetAnnouncementFlags",\
                     "params": {"System": true, "Library": true}, "id": "2"}')

  def send(self, request):
    request["jsonrpc"] = "2.0"
    self.setActionForId(request['id'], request['method'])

    formattedJson = json.write(request)
    print "[SOCKET] Sending " + formattedJson
    self.socket.send(formattedJson)

  def addCallbackForId(self, id, callback):
    self.__callbacks[int(id)] = callback

  def notifyId(self, id, data):
    if (int(id) in self.__callbacks):
        return self.__callbacks[int(id)](data)
    return False
    

  def close(self):
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()
    self.__thread.stop()

  def getId(self):
    return self.__id;

  def getActionForId(self, id):
    return self.__map.get(int(id), None)

  def setActionForId(self, id, action):
    self.__map[int(id)] = action
    self.__id += 1

  def get(self):
    return self.__thread.get()
