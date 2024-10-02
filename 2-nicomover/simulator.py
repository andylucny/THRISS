import time
from functools import partial
import numpy as np
import threading
from yourdfpy import URDF

import os
import requests
import zipfile
import io

def download_simulator(path,url):
    if os.path.exists(path):
        return
    print("downloading",path)
    response = requests.get(url)
    if response.ok:
        file_like_object = io.BytesIO(response.content)
        zipfile_object = zipfile.ZipFile(file_like_object)    
        zipfile_object.extractall(".")

class NicoSimulator:
    
    def __init__(self, urdf_path="nico_upper_ukba.urdf"):
        download_simulator(urdf_path,"http://www.agentspace.org/download/nicosimulator.zip")
        self.urdf_model = URDF.load(urdf_path)
        self.values = {}
        self.thread = threading.Thread(name="agent", target=self.run)
        self.thread.start()
        
    def joint_names(self):
        return self.urdf_model.actuated_joint_names
    
    def joints(self):
        return [self.urdf_model.joint_map[joint_name] for joint_name in self.urdf_model.actuated_joint_names]
        
    def set(self,key,value):
        if key == 'l_shoulder_z' or key == 'head_y' or key == 'l_wrist_z' or key == 'l_wrist_x':
            value = -value
        if key == 'l_wrist_z' or key == 'r_wrist_z':
            value /= 2.0
        if key == 'r_wrist_x':
            if value >= 0:
                value *= -30.0/180.0
            else:
                value *= -50.0/180.0
        if key == 'l_wrist_x':
            if value >= 0:
                value *= -50.0/180.0
            else:
                value *= -30.0/180.0
        if key == 'r_indexfinger_x' or key == 'r_middlefingers_x':
            value = - (value+180) / 2.0
        if key == 'l_indexfinger_x' or key == 'l_middlefingers_x':
            value = (value+180) / 2.0
        if key == 'r_thumb_x' or key == 'l_thumb_x':
            value = value / 4.0 - 135
        if key == 'r_thumb_z':
            value = - value / 4.0 - 195
        if key == 'l_thumb_z':
            value = value / 4.0 - 175
            
        self.values[key] = np.deg2rad(value)

    def getter_callback(self, scene, urdf_model):
        self.urdf_model.update_cfg(configuration=self.values)
        
    def run(self):
        callback = partial(
            self.getter_callback,
            urdf_model=self.urdf_model,
        )
        self.urdf_model._scene.set_camera(
            angles=(np.pi/2,0,np.pi/2),
            distance=0.7,
            center=(0.2,0,0.3),
            resolution=(800,600),
        )
        self.urdf_model.show(
            collision_geometry=False,
            callback=callback,
        )

if __name__ == "__main__":
    import os
    def quit():
        os._exit(0)
        
    simulator = NicoSimulator("nico_upper_ukba.urdf")
    names = simulator.joint_names()
    #simulator.urdf_model._scene.set_camera(angles=(np.pi/2,0,np.pi/2),distance=0.7,center=(0.2,0,0.3),resolution=(800,600))