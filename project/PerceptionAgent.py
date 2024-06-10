import numpy as np
import onnxruntime as ort
import cv2 as cv
import time
from agentspace import Agent, space
from dino import dino
from clip import image_clip

class PerceptionAgent(Agent):

    def __init__(self, nameImage, nameFeatures, namePoints):
        self.nameImage = nameImage
        self.nameFeatures = nameFeatures
        self.namePoints = namePoints
        super().__init__()

    def init(self):
        self.KFs = [ cv.KalmanFilter(4, 2, 0) for _ in range(6) ] 
        for KF in self.KFs:
            KF.transitionMatrix = cv.setIdentity(KF.transitionMatrix)
            KF.measurementMatrix = cv.setIdentity(KF.measurementMatrix)
        self.ticks = cv.getTickCount()
        space.attach_trigger(self.nameImage,self)
        self.t0 = int(time.time())
        self.fs = 0
        self.fps = 0
 
    def senseSelectAct(self):
        frame = space[self.nameImage]
        if frame is None:
            return
            
        _, points, _ = dino(frame)
        
        features = image_clip(frame)
            
        ticks = cv.getTickCount()
        dt = (ticks - self.ticks) / cv.getTickFrequency()
        self.ticks = ticks
        for i, KF in enumerate(self.KFs):
            KF.transitionMatrix[0,2] = dt
            KF.transitionMatrix[1,3] = dt
            prediction = KF.predict()
            if points[i][0] >= 0.0 and points[i][1] >= 0.0:
                correction = KF.correct(np.array(points[i],np.float32))
                points[i] = (correction[0][0],correction[1][0])
            else:
                points[i] = (prediction[0][0],prediction[1][0])
        
        self.fs += 1
        self.t1 = int(time.time())
        if self.t1 > self.t0:
            self.fps = self.fs / (self.t1-self.t0)
            self.fs = 0
            self.t0 = self.t1
            space(validity=2.5)['fps'] = self.fps
        
        space(validity=0.5)[self.nameFeatures] = features
        space(validity=0.5)[self.namePoints] = points

if __name__ == "__main__":

    from CameraAgent import CameraAgent
    camera_agent = CameraAgent('See3CAM_CU135', 0, 'bgr', fps=30, zoom=350)
    
    from dino import dino_visualization
    PerceptionAgent('bgr','clipFeatures','dinoPoints')

    class ViewerAgent(Agent):
    
        def init(self):
            space.attach_trigger('bgr',self)
            
        def senseSelectAct(self):
            frame = space["bgr"]
            if frame is None:
                self.stopped = True
                return

            points = space(default=[None]*6)["dinoPoints"]
            result = dino_visualization(frame,np.zeros(frame.shape[:2],np.uint8),points)
            fps = space["fps"]
            if fps is not None:
                cv.putText(result, f"{fps:1.0f}", (8,25), 0, 1.0, (0, 255, 0), 2)

            cv.imshow('dino & clip',result)
            key = cv.waitKey(1) & 0xff
            if key == 27:
                self.stopped = True
                return
    
    viewer_agent = ViewerAgent()
    time.sleep(20)
    viewer_agent.stop()
    cv.destroyAllWindows()
    camera_agent.stop()
