import threading
import time
    
class Block:

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
            
    def register(self,agent):
        self.registered.append(agent)
    
class Space:
    
    blocks = dict()
    
    def __init__(self):
        pass
        
    def read(name, dflt):
        if name in Space.blocks:
            if Space.blocks[name].valid():
                return Space.blocks[name].value
            else:
                return dflt
        else:
            return dflt
    
    def write(name, value, validity=0.0, priority=0.0):
        #print(name,"=",value)
        if not name in Space.blocks:
            Space.blocks[name] = Block()
        if Space.blocks[name].set(value,validity,priority):
            for agent in Space.blocks[name].registered[:]:
                if agent.stopped:
                    Space.blocks[name].registered.remove(agent)
                else:
                    agent.trigger()
            
    def register(name,agent):
        if not name in Space.blocks:
            Space.blocks[name] = Block()
        Space.blocks[name].register(agent)

class Agent:

    def __init__(self):
        self.stopped = False
        self.event = threading.Event()
        self.timer = None
        self.t = threading.Thread(name="agent", target=self.run)
        self.t.start()
        
    def attach_trigger(self,name):
        Space.register(name,self)
    
    def attach_timer(self,period):
        self.period = period
        self.timer = threading.Timer(self.period,self.timered_trigger)
        self.timer.daemon = True
        self.timer.start()
        
    def timered_trigger(self):
        self.trigger()
        self.attach_timer(self.period)
        
    def receive(self):
        self.event.wait()
        self.event.clear()
    
    def trigger(self):
        self.event.set()
        
    def run(self):
        self.init()
        while not self.stopped:
            self.receive()
            if self.stopped:
                break
            self.senseSelectAct()
        
    def init(self): # to be overiden
        print('I am ready')
    
    def senseSelectAct(self): # to be overiden
        print('I am alive')
        
    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
        self.stopped = True
        self.trigger()
       
