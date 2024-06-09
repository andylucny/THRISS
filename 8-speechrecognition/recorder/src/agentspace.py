import threading
import time
from enum import Enum
from queue import Queue

class Trigger(Enum):
    NORMAL = 0
    NAMES = 1
    NAMES_AND_VALUES = 2
    
class Variable:

    def __init__(self):
        self.value = None
        self.validity = 0.0
        self.priority = 0.0
        self.registered = []
        
    def valid(self):
        if self.value is None:
            return False
        return self.validity == 0.0 or self.validity > time.time()

    def set(self,value,validity,priority):
        if (not self.valid()) or self.priority <= priority:
            self.value = value;
            self.validity = 0.0 if validity == 0.0 else validity + time.time()
            self.priority = priority
            return True
        else:
            return False
            
    def register(self,agent,type=Trigger.NORMAL):
        self.registered.append((agent,type))

    def deregister(self,agent,type):
        self.registered.remove((agent,type))
        
    def triggers(self):
        return self.registered[:]

class SpaceAdaptor:

    def __init__(self, space, default, validity, priority):
        self.validity = validity
        self.priority = priority
        self.default = default
        self.space = space

    def __getitem__(self, name):
        return self.space.read(name, self.default)

    def __setitem__(self, name, value):
        self.space.write(name, value, self.validity, self.priority)
    
class Space:
    spaces = dict()

    def __class_getitem__(cls, name):
        if name not in Space.spaces:
            Space.spaces[name] = Space()
            return Space.spaces[name]

    def __init__(self, definition=""):
        self.variables = dict()
        self.lock = threading.Lock()

    def __call__(self, default=None, validity=0, priority=1.0):
        return SpaceAdaptor(self, default, validity, priority)
    
    def __getitem__(self, name):
        return self.read(name,None)
        
    def __setitem__(self, name, value):
        self.write(name, value)
        
    def read(self, name, dflt):
        with self.lock:
            if name in self.variables:
                if self.variables[name].valid():
                    return self.variables[name].value
                else:
                    return dflt
            else:
                return dflt
    
    def write(self, name, value, validity=0.0, priority=0.0):
        with self.lock:
            if not name in self.variables:
                self.variables[name] = Variable()
            if self.variables[name].set(value,validity,priority):
                for agent, type in self.variables[name].triggers():
                    if agent.stopped:
                        self.variables[name].deregister(agent,type)
                    else:
                        agent.trigger(None if type == Trigger.NORMAL else name,None if type != Trigger.NAMES_AND_VALUES else value)
            
    def attach_trigger(self, name, agent, type=Trigger.NORMAL):
        with self.lock:
            if not name in self.variables:
                self.variables[name] = Variable()
            self.variables[name].register(agent,type)

space = Space[""]

class Agent:

    def __init__(self):
        self.stopped = False
        self.triggered_name = None
        self.timer = None
        self.proxies = Queue()
        self.t = threading.Thread(name="agent", target=self.run)
        self.t.start()
        
    def attach_timer(self, period):
        self.period = period
        self.timer = threading.Timer(self.period,self.timered_trigger)
        self.timer.daemon = True
        self.timer.start()
        
    def timered_trigger(self):
        self.trigger()
        self.attach_timer(self.period)
        
    def receive(self):
        self.triggered_name = self.proxies.get()
    
    def trigger(self, name=None, value=None):
        if value is None:
            if not name in self.proxies.queue:
                self.proxies.put(name)
        else:
            self.proxies.put((name,value))
        
    def run(self):
        self.init()
        while not self.stopped:
            self.receive()
            if self.stopped:
                break
            self.senseSelectAct()
            self.triggered_name = None
        
    def init(self): # to be overiden
        print('I am ready')
    
    def senseSelectAct(self): # to be overiden
        print('I am alive')
        
    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
        self.stopped = True
        self.trigger()
        
    def triggered(self):
        return self.triggered_name
        
if __name__ == "__main__":

    space(validity=2,priority=1)["a"] = 3
    space(priority=0)["a"] = 4
    time.sleep(1)
    print(space(default=-1)["a"])
    time.sleep(1.1)
    print(space(default=-1)["a"])
    space(priority=0)["a"] = 4
    print(space(default=-1)["a"])
    print("-----")
    
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
            space.attach_trigger("a",self)
        def senseSelectAct(self):
            i = space(default=-1)["a"]
            print("agent 2",self.arg,"reads ",i)
    
    a1 = Agent1()
    a2 = Agent2("x")
    print('waiting for 10s')
    time.sleep(10)
    print('done')
    a1.stop()
    time.sleep(3)
    a2.stop()
    