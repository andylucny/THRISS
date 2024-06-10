import numpy as np
import cv2 as cv
from agentspace import Agent, space
import os
import requests
import zipfile
import io
import subprocess
import platform

def download(path,url):
    if os.path.exists(path):
        return
    print("downloading",path)
    response = requests.get(url)
    if response.ok:
        file_like_object = io.BytesIO(response.content)
        zipfile_object = zipfile.ZipFile(file_like_object)    
        zipfile_object.extractall(".")

def initializeCameraControls():
    if platform.system() == "Windows":
        download("v4l2-ctl.exe","https://www.agentspace.org/download/v4l2-ctl.zip")  

initializeCameraControls()

def getCameraDevices():
    command = [ "v4l2-ctl", "--list-devices" ]
    output = subprocess.check_output(command)
    decoded = output.decode()
    devs = []
    ids = []
    assigned = True
    for dev in decoded.split('\n'):
        dev = dev.split('\r')[0].strip()
        if len(dev) == 0:
            continue
        if 'virtual' in dev:
            continue
        if '/dev/video' in dev:
            if assigned:
                continue
            search = re.search('.*/dev/video([0123456789]).*',dev)
            if search is not None:
                id = search.groups()[0]
                if len(devs) > 0:
                    ids[len(devs)-1] = id
            assigned = True
            continue
        id = len(devs)
        devs.append(dev)
        ids.append(id)
        assigned = False

    print('camera devices:')
    for id, dev in zip(ids, devs):
        print(id, dev)
        
    return list(zip(ids,devs))

def setCameraControls(id,controls):
    command = [ "v4l2-ctl", "-d", f"/dev/video{id}" ]
    for control in controls.keys():
        value = controls[control]
        command += [ "-c", f"{control}={value}" ]
    try:
        _ = subprocess.check_output(command)
    except:
        pass

class CameraAgent(Agent):

    def __init__(self, type, order, nameImage, fps=30, zoom=350):
        devices = getCameraDevices()
        self.fullType = type
        self.id = -1
        for id, dev in devices:
            if type in dev:
                if order == 0:
                    self.id = id
                    self.fullType = dev
                order -= 1
        if self.id == -1 and len(devices) > 0:
            self.id, self.fullType = devices[0]
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
        print('selected camera',self.id,self.fullType)
        if platform.system() == "Windows":
            self.camera = cv.VideoCapture(self.id,cv.CAP_DSHOW)
        else:
            self.camera = cv.VideoCapture(self.id)
        if nicoType in self.fullType:
            self.camera.set(cv.CAP_PROP_FPS,self.fps)
        else:
            self.fps = self.camera.get(cv.CAP_PROP_FPS)
            if self.fps == 0:
                self.fps = 10 # to be sure
        print('fps:',self.fps)
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
 
if __name__ == "__main__":
    import time

    camera_agent = CameraAgent('See3CAM_CU135', 0, 'bgr', fps=30, zoom=350)

    class ViewerAgent(Agent):
    
        def init(self):
            space.attach_trigger('bgr',self)
            self.t0 = int(time.time())
            self.fs = 0
            self.fps = 0
            
        def senseSelectAct(self):
            frame = space["bgr"]
            if frame is None:
                self.stopped = True
                return
                
            self.fs += 1
            self.t1 = int(time.time())
            if self.t1 > self.t0:
                self.fps = self.fs / (self.t1-self.t0)
                self.fs = 0
                self.t0 = self.t1

            result = np.copy(frame)
            cv.putText(result, f"{self.fps:1.0f}", (8,25), 0, 1.0, (0, 255, 0), 2)

            cv.imshow('right eye',result)
            key = cv.waitKey(1) & 0xff
            if key == 27:
                self.stopped = True
                return
    
    viewer_agent = ViewerAgent()
    time.sleep(20)
    viewer_agent.stop()
    cv.destroyAllWindows()
    camera_agent.stop()
   