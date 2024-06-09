import socket
import re
from agentspace import Agent,Space

class SenderAgent(Agent):

    def __init__(self,ip,port,name):
        self.ip = ip
        self.port = port
        self.name = name
        super().__init__()
        
    def getline(self):
        while self.buffer.find('\n')==-1:
            self.buffer += self.sock.recv(1024).decode()
        result = re.sub('[\r\n].*','',self.buffer)
        self.buffer = self.buffer[self.buffer.find('\n')+1:]
        return result

    def putline(self,line):
        self.sock.send((line+'\r\n').encode())
        
    def init(self):
        print('sender starting')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip,self.port))
        except ConnectionRefusedError:
            print('router is not running')
            self.stop()
        self.attach_trigger(self.name)
        self.putline('connect')
  
    def senseSelectAct(self):
        text = Space.read(self.name,'')
        self.putline(text)
