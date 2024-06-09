import os
import time
import cv2 as cv
import numpy as np 
from agentspace import space, Agent
from clip import image_clip, cosine_similarity

def quit():
    os._exit(0)

# Initializing video capture agent
class CameraAgent(Agent):
    def init(self):
        camera = cv.VideoCapture(0,cv.CAP_DSHOW)
        while True:
            _, frame = camera.read()
            space["bgr"] = frame
            if self.stopped:
                break
        
camera_agent = CameraAgent()
while space["bgr"] is None:
    time.sleep(0.25)

if os.path.exists('keys.npy'):
    keys = np.loadtxt('keys.npy')
else:
    keys = None

threshold = 0.7
while True:
    frame = space["bgr"]
    if frame is None:
        break

    t0 = time.time()
    
    query = image_clip(frame)
    
    t1 = time.time()
    fps = 1.0/(t1-t0)

    if keys is not None:
        probabilities = cosine_similarity(query, keys)
        index = np.argmax(probabilities)
        text = f"{index:1d}, {probabilities[index]:1.2f}%"
        if probabilities[index] > threshold:
            color = (0, 0, 255)
        else:
            color = (80, 80, 80)
        cv.putText(frame, text, (frame.shape[1]//2, frame.shape[0]//2), 0, 2.0, (0, 0, 255), 2)
    
    cv.putText(frame, f"{fps:1.2f}", (8,25), 0, 1.0, (0, 255, 0), 2)

    cv.imshow('clip',frame)
    key = cv.waitKey(1) & 0xff
    if key == 27:
        break
    elif key == ord('k'):
        keys = np.array(query) if keys is None else np.vstack([keys,query])
        np.savetxt('keys.npy',keys)

cv.destroyAllWindows()
camera_agent.stop()