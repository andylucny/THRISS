import numpy as np
import time
from agentspace import Agent, space

from nicomover import setAngle, getAngle, enableTorque, release
from headlimiter import head_z_limits

class LookAroundAgent(Agent):

    def __init__(self, namePoints, nameSupress):
        self.namePoints = namePoints
        self.nameSupress = nameSupress
        super().__init__()

    def init(self):
        enableTorque(["head_z","head_y"])
        setAngle("head_z",0.0,0.05)
        setAngle("head_y",-25.0,0.05)
        time.sleep(2.0)
        space.attach_trigger(self.namePoints,self)

    def senseSelectAct(self):
    
        if space(default=False)[self.nameSupress]:
            return
    
        points = space[self.namePoints]
        if points is None:
            return
            
        point = points[2]
        if point is None:
            return
        
        x, y = point
        
        head_x = getAngle("head_z")
        head_y = getAngle("head_y")
        
        _, limit_x = head_z_limits(head_y)
        
        reset_x, reset_y = False, False
        if np.abs(head_x) > 40:
            if np.random.rand() > 0.95:
                reset_x = True
        else:
            if np.random.rand() > 0.995:
                reset_x = True
        if head_y > 20: #15
            if np.random.rand() > 0.95:
                reset_y = True
        else:
            if np.abs(head_x) > 5:
                if np.random.rand() > 0.995:
                    reset_y = True
        
        if reset_x:
            delta_degrees_x = -head_x
            #print("RESET X")
        else:
            delta_degrees_x = np.arctan2((0.5-x)*np.tan(20*np.pi/180),0.5)*180/np.pi
        if reset_y:
            delta_degrees_y = -head_y - 25
            #print("RESET Y")
        else:
            delta_degrees_y = np.arctan2((0.5-y)*np.tan(20*np.pi/180),0.5)*180/np.pi
        
        if head_y + delta_degrees_y <= -limit_x+1:
            delta_degrees_y = 0.0
        if head_y + delta_degrees_y >= limit_x-1:
            delta_degrees_y = 0.0
        
        angular_speed = 0.04
        limit = 2.0 
        
        if np.abs(delta_degrees_x) > limit:
            setAngle("head_z", head_x + delta_degrees_x, angular_speed)
        if np.abs(delta_degrees_y) > limit:
            setAngle("head_y", head_y + delta_degrees_y, angular_speed)

        time.sleep(max(np.abs(delta_degrees_x),np.abs(delta_degrees_y))/(1000*angular_speed))
