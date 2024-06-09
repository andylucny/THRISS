import cv2 as cv
from agentspace import Agent, space
import time

import subprocess

def getCameraDevices():
    command = [ "v4l2-ctl", "--list-devices" ]
    devs = subprocess.check_output(command)
    return [ dev.split('\r')[0] for dev in devs.decode().split('\n') if len(dev) > 0 and (not 'virtual' in dev) and (not '/dev/video' in dev) ]

def setCameraControls(id,controls):
    command = [ "v4l2-ctl", "-d", f"/dev/video{id}" ] #TBD id and video id do not matching on Linux
    for control in controls.keys():
        value = controls[control]
        command += [ "-c", f"{control}={value}" ]
    try:
        _ = subprocess.check_output(command)
    except:
    	pass

class CameraAgent(Agent):

    def __init__(self, type, order, nameImage, fps=30, zoom=350):
        self.type = type
        self.fullType = type
        devs = getCameraDevices()
        self.id = -1
        for id, dev in enumerate(devs):
            print('device',dev,'?',type)
            if type in dev:
                if order == 0:
                    self.id = id*2
                    self.fullType = dev
                    print('found')
                order -= 1
        if self.id == -1 and len(devs) > 0:
            self.id = 0
            self.fullType = devs[0]
        self.nameImage = nameImage
        self.fps = fps
        self.zoom = zoom
        super().__init__()
        
    def init(self):
        if self.id == -1:
            self.stop()
            return
        nicoType = 'See3CAM_CU135'
        if nicoType in self.fullType:
            setCameraControls(self.id,{'zoom_absolute':self.zoom,'tilt_absolute':0,'pan_absolute':0})
        print('camera',self.fullType,self.id)
        self.camera = cv.VideoCapture(self.id) #,cv.CAP_DSHOW) #,
        #if nicoType in self.fullType:
        self.camera.set(cv.CAP_PROP_FPS,self.fps)
        while not self.stopped:
            # Grab a frame
            ret, img = self.camera.read()
            if not ret:
                #self.stop()
                #return
                continue
            
            # sample it onto blackboard
            space(validity=3.0/self.fps)[self.nameImage] = img
            
        self.camera.release()
 
    def senseSelectAct(self):
        pass

camera_agent = CameraAgent('See3CAM_CU135',0,'bgr')
while space["bgr"] is None: 
    time.sleep(0.25) # wait for camera

while True:
    frame = space["bgr"]
    if frame is None:
        break

    cv.imshow('dino',frame)
    key = cv.waitKey(1) & 0xff
    if key == 27:
        break

cv.destroyAllWindows()
camera_agent.stop()

