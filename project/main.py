import time
import os
import signal
import re
import numpy as np
import cv2 as cv
from agentspace import Agent, space, Trigger

from nicomover import setAngle, getAngle, enableTorque, disableTorque, park, release
from nicomover import current_posture, move_to_posture, load_movement, play_movement

from dino import dino_visualization
from clip import image_clip, text_clip, cosine_similarity, clip

def quit():
    release()
    os._exit(0)

def signal_handler(signal, frame): 
    quit()
    
signal.signal(signal.SIGINT, signal_handler)

from CameraAgent import CameraAgent
from PerceptionAgent import PerceptionAgent
from LookAroundAgent import LookAroundAgent
from SpeakerAgent import SpeakerAgent
from ReceiverAgent import ReceiverAgent

CameraAgent('See3CAM_CU135',1,'robotEye',fps=10,zoom=350) # right eye
time.sleep(1)
PerceptionAgent('robotEye','clipFeatures','dinoPoints')
time.sleep(1)
LookAroundAgent('dinoPoints','dontLook')
time.sleep(1)
SpeakerAgent('tospeak')
time.sleep(1)
ReceiverAgent(7171,'listened')
time.sleep(1)

class ControlAgent(Agent):
    
    def init(self):
        self.keys = np.loadtxt('mykeys.npy')
        space.attach_trigger('clipFeatures',self,Trigger.NAMES)
        space.attach_trigger('listened',self,Trigger.NAMES)

    def speak(self, text):
        space(validity=0.1)['tospeak'] = text

    def dontLook(self):
        space['dontLook'] = True

    def lookAround(self):
        space['dontLook'] = False

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

    def senseSelectAct(self):
        changed = self.triggered()
        if changed == 'clipFeatures':
        
            self.features = space['clipFeatures']
            
            frame = space['robotEye']
            if frame is not None:

                points = space(default=[None]*6)["dinoPoints"]
                result = dino_visualization(frame,np.zeros(frame.shape[:2],np.uint8),points)
                fps = space["fps"]
                if fps is not None:
                    cv.putText(result, f"{fps:1.0f}", (8,25), 0, 1.0, (0, 255, 0), 2)

                cv.imshow('NICO project',result)
                key = cv.waitKey(1) & 0xff
                if key == 27:
                    self.stopped = True
                    quit()           
            
        elif changed == 'listened':
            text = space['listened'].strip().lower()
            print('listened text:', text)
            if self.match(r'is this (.*)',text):
                caption = 'This is ' + self.matched()[0].replace('?','.')
                query = text_clip(caption)
                text_probabilities = cosine_similarity(query,self.keys)
                text_index = np.argmax(text_probabilities)
                image_probabilities = cosine_similarity(self.features,self.keys)
                image_index = np.argmax(image_probabilities)
                self.dontLook()
                setAngle('head_z',0.0)
                setAngle('head_y',0.0)
                if text_index == image_index:
                    # yes
                    self.speak('yes')
                    movement = [
                        {'head_y':-20},
                        {'head_y':20},
                        {'head_y':-20},
                        {'head_y':20},
                        {'head_y':-20},
                        {'head_y':20},
                    ]
                else:
                    self.speak('no')
                    movement = [
                        {'head_z':-30},
                        {'head_z':30},
                        {'head_z':-30},
                        {'head_z':30},
                        {'head_z':-30},
                        {'head_z':30},
                    ]
                    # No
                durations = [0.5,0.5,0.5,0.5,0.5,0.5]
                play_movement(movement,durations)
                self.lookAround()

ControlAgent()
              