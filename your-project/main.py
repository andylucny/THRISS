import time
import os
import signal
from agentspace import Agent, space
from ExperimentAgent import close

def quit():
    #Agent.stopAll()
    close()
    os._exit(0)

# exit on ctrl-c
def signal_handler(signal, frame):
    quit()
    
signal.signal(signal.SIGINT, signal_handler)

from download import download_all
download_all()

from ExperimentAgent import ExperimentAgent
from GuiAgent import GuiAgent
from TouchAgent import TouchAgent
from CameraAgent import CameraAgent
from RecorderAgent import RecorderAgent
from SafetyAgent import SafetyAgent
from FaceAgent import FaceAgent
from ActionAgent import ActionAgent

GuiAgent() # writes 'experiment', 'stop' reads 'humanImage', 'robotImage', 'robotEye', 'robotWideFOV'
time.sleep(1)
TouchAgent() # writes 'touch', 'stop', 'experiment', 'touchImage' reads 'emulated'
time.sleep(1)
ExperimentAgent()
time.sleep(1)
CameraAgent('HD Pro Webcam C920',1,'humanImage',fps=10)
time.sleep(1)
CameraAgent('HD Pro Webcam C920',0,'robotImage',fps=10)
time.sleep(1)
CameraAgent('See3CAM_CU135',1,'robotEye',fps=10,zoom=350) # right eye
time.sleep(1)
CameraAgent('See3CAM_CU135',0,'robotWideFOV',fps=10,zoom=170) # left eye
time.sleep(1)
RecorderAgent() # reads 'humanImage', 'robotImage', 'robotEye', 'touchImage'
time.sleep(1)
SafetyAgent()
time.sleep(1)
#FaceAgent('robotWideFOV','face position','face','emotion','face point') # face detector
#time.sleep(1)
ActionAgent('face point') # turn to shown objects
time.sleep(1)
