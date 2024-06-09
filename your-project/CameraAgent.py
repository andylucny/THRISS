import cv2 as cv
from agentspace import Agent, space

import subprocess

def getCameraDevices():
    command = [ "v4l2-ctl", "--list-devices" ]
    devs = subprocess.check_output(command)
    return [ dev for dev in devs.decode().split('\r\n') if len(dev) > 0 and (not 'virtual' in dev) ]

def setCameraControls(id,controls):
    command = [ "v4l2-ctl", "-d", f"/dev/video{id}" ]
    for control in controls.keys():
        value = controls[control]
        command += [ "-c", f"{control}={value}" ]
    _ = subprocess.check_output(command)

class CameraAgent(Agent):

    def __init__(self, type, order, nameImage, fps=30, zoom=350):
        self.type = type
        self.fullType = type
        self.id = -1
        for id, dev in enumerate(getCameraDevices()):
            if type in dev:
                if order == 0:
                    self.id = id
                    self.fullType = dev
                order -= 1
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
        self.camera = cv.VideoCapture(self.id,cv.CAP_DSHOW)
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

