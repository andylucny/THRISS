import re
import os
import signal
from agentspace import Agent, space
from receiver import ReceiverAgent

def quit():
    os._exit(0)
    
# exit on ctrl-c
def signal_handler(signal, frame):
    quit()
    
signal.signal(signal.SIGINT, signal_handler)

import platform
if platform.system() == "Windows":
    import io
    import requests
    import zipfile

    def download_zipfile(path,url):
        if os.path.exists(path):
            return
        print("downloading",url)
        response = requests.get(url)
        if response.ok:
            file_like_object = io.BytesIO(response.content)
            zipfile_object = zipfile.ZipFile(file_like_object)    
            zipfile_object.extractall(".")
        print("downloaded")
        
    def download_recorder():
        download_zipfile('recorder/binaries','http://www.agentspace.org/download/recorder.zip')

    download_recorder()
    print('use recorder.bat')
else:
    os.chmod('recorder.sh', 0o777)
    print('use ./recorder.sh')

class ListenerAgent(Agent):

    def match(self,pattern,text):
        search = re.search(pattern,text)
        if search is None:
            self.groups = []
            return False
        else:
            self.groups = search.groups()
            return True
    
    def matched(self):
        return self.groups

    def __init__(self,name):
        self.name = name
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.name,self)
 
    def senseSelectAct(self):
        text = space(default='')[self.name]
        text = text.strip().lower()
        if len(text) > 0:
            print("->",text)
            if text == 'connect':
                print('--- recorder connected ---')
            elif self.match(r'say (.*)',text):
                print('I am asked to say:', self.matched()[0])
            
ReceiverAgent(7171,'text')
ListenerAgent('text')
