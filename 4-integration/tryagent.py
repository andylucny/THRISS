import os 
def quit(): # for the interactive mode
    os._exit(0)

import signal 
def signal_handler(signal, frame):  
    quit()

signal.signal(signal.SIGINT, signal_handler) # for ctrl-c in the interactive mode

from agentspace import space, Agent

class Agent1(Agent):

    def init(self):
        self.attach_timer(1)
        self.i = 0
        
    def senseSelectAct(self):
        print("agent 1 writes ",self.i)
        space["a"] = self.i
        self.i += 1

class Agent2(Agent):

    def __init__(self,arg):
        self.arg = arg
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.arg,self)
        
    def senseSelectAct(self):
        i = space(default=-1)[self.arg]
        print("agent 2",self.arg,"reads ",i)

a1 = Agent1()
a2 = Agent2("a")

import platform
import sys
if platform.system() == "Windows":
    if sys.flags.interactive: 
        print("press cltr-break or ctrl-c to stop")
    else:
        print("press ctrl-break to stop")
else:
    print("press ctrl-c to stop")
