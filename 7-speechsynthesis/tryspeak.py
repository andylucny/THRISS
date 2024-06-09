import os
import time
from speak import speak
from agentspace import space, Agent, Trigger

def quit():
    os._exit(0)

class SpeakerAgent(Agent):

    def __init__(self, nameText):
        self.nameText = nameText
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.nameText,self,Trigger.NAMES_AND_VALUES)
        
    def senseSelectAct(self):
        _, text = self.triggered()
        speak(text)
 
SpeakerAgent('text-to-speak')
time.sleep(1)

def myspeak(text):
    space(validity=0.1)['text-to-speak'] = text

myspeak('I am speaking from another thread')

myspeak('one')
myspeak('two')
myspeak('three')

