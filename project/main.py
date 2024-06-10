import time
import os
import signal
from agentspace import Agent, space

from nicomover import setAngle, getAngle, enableTorque, disableTorque, park, release
from nicomover import current_posture, move_to_posture, load_movement, play_movement

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

CameraAgent('See3CAM_CU135',1,'robotEye',fps=10,zoom=350) # right eye
time.sleep(1)
PerceptionAgent('robotEye','clipFeatures','dinoPoints')
time.sleep(1)
LookAroundAgent('dinoPoints','dontLook')
time.sleep(1)
