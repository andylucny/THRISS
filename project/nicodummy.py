import time
import threading
import numpy as np
from simulator import NicoSimulator

class DummyRobot():
    
    def __init__(self):
        self.joints = { # standard position
            'l_shoulder_z':0.0,
            'l_shoulder_y':1.0,
            'l_arm_x':0.0,
            'l_elbow_y':91.0,
            'l_wrist_z':-4.0,
            'l_wrist_x':-56.0,
            'l_thumb_z':-57.0,
            'l_thumb_x':-180.0,
            'l_indexfinger_x':-180.0,
            'l_middlefingers_x':-180.0,
            'r_shoulder_z':0.0,
            'r_shoulder_y':1.0,
            'r_arm_x':0.0,
            'r_elbow_y':91.0,
            'r_wrist_z':-5.0,
            'r_wrist_x':-56.0,
            'r_thumb_z':-57.0,
            'r_thumb_x':-180.0,
            'r_indexfinger_x':-180.0,
            'r_middlefingers_x':-180.0,
            'head_z':1.0,
            'head_y':1.0
        }
        self.ranges = {
            'head_z':(-90.0,90.0),
            'head_y':(-40.0,30.0),
            'l_shoulder_z':(-30.0,80.0),
            'l_shoulder_y':(-30.0,180.0),
            'l_arm_x':(-0.0,70.0),
            'l_elbow_y':(50.0,180.0),
            'r_shoulder_z':(-30.0,80.0),
            'r_shoulder_y':(-30.0,180.0),
            'r_arm_x':(-0.0,70.0),
            'r_elbow_y':(50.0,180.0),
            'r_wrist_z':(-180.0,180.0),
            'r_wrist_x':(-180.0,180.0),
            'r_thumb_z':(-180.0,180.0),
            'r_thumb_x':(-180.0,180.0),
            'r_indexfinger_x':(-180.0,180.0),
            'r_middlefingers_x':(-180.0,180.0),
            'l_wrist_z':(-180.0,180.0),
            'l_wrist_x':(-180.0,180.0),
            'l_thumb_z':(-180.0,180.0),
            'l_thumb_x':(-180.0,180.0),
            'l_indexfinger_x':(-180.0,180.0),
            'l_middlefingers_x':(-180.0,180.0)
        }
        self.simulator = NicoSimulator()
        self.destinations = {}
        self.speeds = {}
        time.sleep(1)
        for dof in self.joints:
            self.physicalSetAngle(dof, self.joints[dof])
        time.sleep(8) # wait for simulator
        self.t = threading.Thread(name="motors", target=self.run)
        self.t.start()
    
    def getJointNames(self):
        return [
            'head_z', 'head_y',
            'r_shoulder_z', 'r_shoulder_y', 'r_arm_x', 'r_elbow_y', 
            'l_shoulder_z', 'l_shoulder_y', 'l_arm_x', 'l_elbow_y', 
            'r_wrist_z', 'r_wrist_x', 'r_thumb_z', 'r_thumb_x', 'r_indexfinger_x', 'r_middlefingers_x', 
            'l_wrist_z', 'l_wrist_x', 'l_thumb_z', 'l_thumb_x', 'l_indexfinger_x', 'l_middlefingers_x', 
        ]
        
    def getAngleLowerLimit(self, dof):
        return self.ranges[dof][0]
    
    def getAngleUpperLimit(self, dof):
        return self.ranges[dof][1]
    
    def getAngle(self, dof):
        return self.joints[dof]
        
    def physicalSetAngle(self, dof, angle):
        self.joints[dof] = angle
        self.simulator.set(dof, angle)

    def setAngle(self, dof, angle, speed):
        self.speeds[dof] = speed
        self.destinations[dof] = angle        
        
    def enableTorque(self, dof):
        pass
    
    def disableTorque(self, dof):
        pass
    
    def getPalmSensorReading(self, dof):
        return 10.0

    def run(self):
        dt = 0.04
        while True:
            time.sleep(dt)
            dofs = list(self.destinations.keys())
            for dof in dofs:
                current = self.joints[dof]
                destination = self.destinations[dof]
                dir = np.sign(destination - current)
                dangle = dt*self.speeds[dof]*1260
                if np.abs(current - destination) <= dangle:
                    angle = destination
                    self.destinations.pop(dof,None)
                    self.speeds.pop(dof,None)
                else:
                    angle = current + dir*dangle
                self.physicalSetAngle(dof, angle)
