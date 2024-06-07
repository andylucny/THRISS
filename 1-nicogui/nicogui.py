import time
import time
import os
import requests
import io
import signal
import PySimpleGUI as sg
import cv2
import numpy as np
import chime ; chime.theme('zelda')
try:
    from nicomotion.Motion import Motion

    def download_config(path,url):
        if os.path.exists(path):
            return
        print("downloading",path)
        response = requests.get(url+path)
        if response.ok:
            print("saving",path)
            open(path,"wb").write(response.content)
            
    download_config("nico_humanoid_upper_rh7d_ukba.json","http://www.agentspace.org/download/")
except:
    print("Nico robot will be simulated")
from nicocameras import NicoCameras, image_shift_xy
from nicodummy import DummyRobot
from headlimiter import head_z_limits

def quit():
    os._exit(0)

# exit on ctrl-c
def signal_handler(signal, frame):
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

motorConfig = './nico_humanoid_upper_rh7d_ukba.json'
try:
    robot = Motion(motorConfig=motorConfig)
except:
    robot = DummyRobot()
    print('motors are not operational')

defaultSpeed = 0.04*0.5

def enabledTorque(jointName):
    global robot
    if hasattr(robot, jointName):
        motor = getattr(robot, jointName)
        return motor.compliant
    else:
        return True

def getRange(joint):
    global robot
    low_ = robot.getAngleLowerLimit(joint)
    high_ = robot.getAngleUpperLimit(joint)
    low = min(round(low_,-1),round(high_,-1))
    high = max(round(low_,-1),round(high_,-1))
    defval = robot.getAngle(joint)
    return low, high, defval
    
dofs = []
dofs += [ dof for dof in robot.getJointNames() if dof.startswith('l_') ] 
dofs += [ dof for dof in robot.getJointNames() if dof.startswith('r_') ] 
dofs += [ dof for dof in robot.getJointNames() if dof.startswith('head_') ] 
    
eyes = [ 'left-eye', 'right-eye' ]
controls = [ 'Left-zoom', 'Left-tilt', 'Left-pan', 'Right-zoom', 'Right-tilt', 'Right-pan' ]

groups = {}
groups['left-arm'] = [k for k in dofs[:6]]
groups['left-hand'] = [k for k in dofs[6:10]]
groups['right-arm'] = [k for k in dofs[10:16]]
groups['right-hand'] = [k for k in dofs[16:20]]
groups['head'] = [k for k in dofs[20:]]

sg.theme("LightGreen")

slider_v = 36 #32
slider_h = 10

def side_layout(kind='Left', id=0): #id=10
    layout = []
    layout.append([
        sg.Text(kind, size=(5, 1), justification="left"),
        sg.Text("", size=(5, 1), justification="left", key=kind+"-FPS"),
        sg.Checkbox('+', default=False, key='concern-'+kind+'Cross', enable_events=True),
        sg.Text("palm", size=(5, 1), justification="left"),
        sg.Slider((0,255), 10, 1, orientation="h", size=(slider_v//2, slider_h), key=kind+'-palm', enable_events=False)
    ])
    layout.append([
        sg.Column([
        [
            sg.Text('zoom         tilt       pan', size=(18, 1), justification="left")
        ],
        [
            sg.Slider((100,800), 100, 1, orientation="v", size=(slider_v//3, slider_h), key=kind+'-zoom'),
            sg.Slider((-180,180), 0, 1, orientation="v", size=(slider_v//3, slider_h), key=kind+'-tilt'),
            sg.Slider((-180,180), 0, 1, orientation="v", size=(slider_v//3, slider_h), key=kind+'-pan')
        ]
        ], vertical_alignment='middle'), 
        sg.Image(filename="", key=kind+"-EYE") 
    ])
    #texts = ["Arm","","","Elbow","Wrist","","Thumb","","Forefinger","Little fingers"]
    for i in range(10):
        key = dofs[id+i]
        minVal, maxVal, defVal = getRange(key) 
        layout.append([ 
            #sg.Text(texts[i], size=(15, 1)), 
            sg.Text(key, size=(19, 1)), 
            sg.Slider((minVal, maxVal), defVal, 1, orientation="h", size=(slider_v, slider_h), key=key)
        ])
    return layout
    
def addons_layout(id=20):
    layout = [
        [ 
            sg.Text("Units: degrees", size=(15, 1))
        ],    
        [ 
            sg.Text("Torque", size=(10, 1)), 
            sg.Radio("Off", "Torque", False, size=(8, 1), key="Torque-Off", enable_events=True), 
            sg.Radio("On", "Torque", True, size=(8, 1), key="Torque-On", enable_events=True) 
        ],
        [ 
            sg.Text("Synchronize", size=(10, 1)), 
            sg.Radio("Off", "Synchro", True, size=(5, 1), key="Synchro-Off", enable_events=True), 
            sg.Radio("On", "Synchro", False, size=(4, 1),key="Synchro-On", enable_events=True),
            sg.Radio("Reverse", "Synchro", False, size=(7, 1),key="Synchro-Reverse", enable_events=True) 
        ]
    ]
    layout.append([ sg.HSeparator() ])
    texts = [dofs[-2], dofs[-1]]
    for i in range(2):
        key = dofs[id+i]
        minVal, maxVal, defVal = getRange(key)
        layout.append([ sg.Slider((minVal, maxVal), defVal, 1, orientation="h", size=(slider_v, slider_h), key=key) ])
        layout.append([ sg.Text(texts[i], size=(10, 1))])
    layout.append([ sg.HSeparator() ])
    layout.append([ sg.Push(), sg.Button("Set default position", size=(20, 1)) ])    
    layout.append([ sg.HSeparator() ])
    layout.append([ 
        sg.Text("Capture", size=(6, 1)), 
        sg.Text("0", size=(4,1), key="Captured"),
        sg.Push(), 
        sg.Radio("Pose", "Mode of Recording", True, size=(5, 1), key="Mode-Pose", enable_events=True),
        sg.Radio("Movement", "Mode of Recording", False, size=(10, 1), key="Mode-Movement", enable_events=True)
    ])
    layout.append([  
        sg.Text("Period", size=(6, 1)),
        sg.Slider((1,5000), 1000, 1, orientation="h", size=(20, 10), key="Period", enable_events=True),
        sg.Text("ms", size=(2, 1))
    ])
    layout.append([
        sg.Button("Start", size=(5, 1), key="Start Recording"),
        sg.Button("Stop", size=(5, 1), key="Stop Recording"),
        sg.Input(key="Save Recording", enable_events=True, visible=False),
        sg.FileSaveAs(button_text='Save', size=(5, 1), initial_folder=os.getcwd(), tooltip="save recorded data into a file", file_types=(("text files", "*.txt"),), target="Save Recording"),
        sg.Input(key="Load Recording", enable_events=True, visible=False),
        sg.FileBrowse(button_text='Load', size=(5, 1), initial_folder=os.getcwd(), tooltip="load recorded data from a file", file_types=(("text files", "*.txt"),), target="Load Recording"),
        sg.Button("Replay", size=(5, 1), key="Replay Recording")
    ])  
    layout.append([ 
        sg.Checkbox('left arm  ', default=True, key='concern-left-arm', enable_events=True), 
        sg.Checkbox('left hand ', default=True, key='concern-left-hand', enable_events=True), 
        sg.Checkbox('head', default=True, key='concern-head', enable_events=True),
        sg.Push(), 
        sg.Text("0", size=(4,1), key="Replayed", visible=False) 
    ])
    layout.append([ 
        sg.Checkbox('rigth arm', default=True, key='concern-right-arm', enable_events=True), 
        sg.Checkbox('right hand', default=True, key='concern-right-hand', enable_events=True), 
        sg.Checkbox('left eye', default=False, key='concern-left-eye', enable_events=True),
        sg.Checkbox('right eye', default=False, key='concern-right-eye', enable_events=True)
    ])
    layout.append([ 
        sg.Checkbox('beep', default=True, key='beep', enable_events=True)
    ])
    layout.append([ sg.VPush() ])
    layout.append([ sg.Push(), sg.Button("Exit", size=(10, 1)) ])
    return layout
       
layout = [[
    sg.Column(side_layout('Left',0), vertical_alignment='top'), 
    sg.VSeparator(),
    sg.Column(side_layout('Right',10), vertical_alignment='top'),      
    sg.VSeparator(),
    sg.Column(addons_layout(20), vertical_alignment='top', expand_y=True)   
]]

cameras = NicoCameras()

# Create the window and show it without the plot
window = sg.Window("Nico control GUI", layout, finalize=True)

for i in range(2):
    window[controls[0+i*3]].update(value = list(cameras.getZoom())[i])
    window[controls[1+i*3]].update(value = list(cameras.getTilt())[i])
    window[controls[2+i*3]].update(value = list(cameras.getPan())[i])

window.bind("<Escape>", "Exit")
for k in dofs: 
    window[k].bind('<ButtonRelease-1>', ' Release')
    window[k].bind('<ButtonPress-1>', ' Press')
for k in controls: 
    window[k].bind('<ButtonRelease-1>', ' Release')
    window[k].bind('<ButtonPress-1>', ' Press')
window.bind("<minus>", "Current-")
window.bind("<Key-+>", "Current+")
window.bind("<Alt-s>", "Current-")
window.bind("<Alt-a>", "Current+")

for k in dofs:
    robot.enableTorque(k)
torque = True

synchro = 0
def synchronized(key):
    if key.startswith('l_'):
        return 'r'+key[1:]
    elif 'r_' in key:
        return 'l'+key[1:]
    return key

def synchronizable(key,basekey):
    return (basekey.startswith('l_') and key.startswith('r_')) or (basekey.startswith('r_') and key.startswith('l_'))
    
def cross(img):
    h, w = img.shape[:2]
    cv2.line(img,(w//2,0),(w//2,h-1),(0,0,255),1)
    cv2.line(img,(0,h//2),(w-1,h//2),(0,0,255),1)
    
def crossAddons(img,d,s):
    h, w = img.shape[:2]
    dx, dy = d
    dx = int(dx//2*s)
    dy = int(dy//2*s)
    cv2.line(img,(w//2+dx,h//3),(w//2+dx,2*h//3),(0,255,0),1)    
    cv2.line(img,(w//3,h//2+dy),(2*w//3,h//2+dy),(0,255,0),1)

try:

    beep = True
    period = 1000
    mode = True #pose
    window["Stop Recording"].update(text='Next')
    record = False
    recorded = []
    recorded_images = []
    concerned_dofs = []
    window["Captured"].update(value=str(len(recorded)))
    replaying = False
    replay = -1
    current = dofs[0]
    newValue = None
    pressed = { k:False for k in dofs }
    pressed.update({ k:False for k in controls })
    concerned = { k:True for k in dofs }
    concerned.update({ k:False for k in eyes })
    concerned.update({ 'LeftCross':False, 'RightCross':False })
    t0 = int(time.time()*1000/period)
    while True:
        event, values = window.read(timeout=1)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Set default position":
            if not torque:
                torque = True
                window["Torque-On"].update(value=True)
                for k in dofs:
                    robot.enableTorque(k)
            #for k in dofs:
            #    robot.toSafePosition() # initial position
            safe = { # standard position
                'l_shoulder_z':0.0,
                'l_shoulder_y':0.0,
                'l_arm_x':0.0,
                'l_elbow_y':89.0,
                'l_wrist_z':0.0,
                'l_wrist_x':-56.0,
                'l_thumb_z':-57.0,
                'l_thumb_x':-180.0,
                'l_indexfinger_x':-180.0,
                'l_middlefingers_x':-180.0,
                'r_shoulder_z':0.0,
                'r_shoulder_y':0.0,
                'r_arm_x':0.0,
                'r_elbow_y':89.0,
                'r_wrist_z':0.0,
                'r_wrist_x':-56.0,
                'r_thumb_z':-57.0,
                'r_thumb_x':-180.0,
                'r_indexfinger_x':-180.0,
                'r_middlefingers_x':-180.0,
                'head_z':0.0,
                'head_y':0.0
            }
            for k in safe.keys():
                robot.setAngle(k,safe[k],defaultSpeed)

    #    if event != '__TIMEOUT__':
    #    print(event)
            
        if 'Press' in event:
            for k in dofs + controls:
                if k in event:
                    #print(k,' pressed')
                    pressed[k] = True
        elif 'Release' in event:
            for k in dofs + controls:
                if k in event:
                    #print(k,' released',values[k])
                    pressed[k] = False
                    if k in dofs:
                        if enabledTorque(k): #torque:
                            ks = synchronized(k)
                            if synchro == 0 or synchro == 1 or ks == k:
                                #print('set',k,'to',values[k])
                                robot.setAngle(k,values[k],defaultSpeed)
                            if (synchro == 1 or synchro == -1) and ks != k:
                                #print('set',ks,'to',values[k])
                                robot.setAngle(ks,values[k],defaultSpeed)
                    else:
                        i = 0 if k.startswith('Left-') else 1
                        value = int(values[k])
                        if 'zoom' in k:
                            #print('zoom camera',i,'to',value)
                            cameras.setZoom(i,value)
                            if synchro:
                                #print('zoom camera',1-i,'to',value)
                                cameras.setZoom(1-i,value)
                        elif 'tilt' in k:
                            #print('tilt camera',i,'to',value)
                            cameras.setTilt(i,value)
                            if synchro:
                                #print('tilt camera',1-i,'to',value)
                                cameras.setTilt(1-i,value)
                        elif 'pan' in k:
                            #print('pan camera',i,'to',value)
                            cameras.setPan(i,value)
                            if synchro:
                                #print('pan camera',1-i,'to',value)
                                cameras.setPan(1-i,value)
                    current = k
                    newValue = None
        elif 'Current' in event:
            #print('current',event)
            diff = -1.0 if event[-1] == '-' else 1.0
            if newValue is None:
                newValue = values[current]
            if current in dofs:
                if enabledTorque(current): #torque:
                    newValue += diff
                    minVal, maxVal, _ = getRange(current)
                    newValue = max(min(newValue,maxVal),minVal)
                    window[current].update(value=newValue)
                    currents = synchronized(current)
                    if synchro == 0 or synchro == 1 or currents == current:
                        #print('set',current,'to',newValue)
                        robot.setAngle(current,newValue,defaultSpeed)
                    if (synchro == 1 or synchro == -1) and currents != current:
                        #print('set',currents,'to',newValue)  
                        robot.setAngle(currents,newValue,defaultSpeed)
            else:
                i = 0 if current.startswith('Left-') else 1
                orgValue = newValue
                newValue += diff
                if 'zoom' in current:
                    newValue = max(min(newValue,800.0),100.0)
                    if orgValue != newValue:
                        #print('zoom camera',i,'to',value)
                        cameras.setZoom(i,int(newValue))
                        if synchro:
                            #print('zoom camera',1-i,'to',value)
                            cameras.setZoom(1-i,int(newValue))
                        window[current].update(value=newValue)
                elif 'tilt' in current:
                    newValue = max(min(newValue,180.0),-180.0)
                    if orgValue != newValue:
                        #print('tilt camera',i,'to',value)
                        cameras.setTilt(i,int(newValue))
                        if synchro:
                            #print('tilt camera',1-i,'to',value)
                            cameras.setTilt(1-i,int(newValue))
                        window[current].update(value=newValue)
                elif 'pan' in current:
                    newValue = max(min(newValue,180.0),-180.0)
                    if orgValue != newValue:
                        #print('pan camera',i,'to',value)
                        cameras.setPan(i,int(newValue))
                        if synchro:
                            #print('pan camera',1-i,'to',value)
                            cameras.setPan(1-i,int(newValue))
                        window[current].update(value=newValue)
        elif event == 'Torque-On':
            torque = True
            print('torque on')
            for k in dofs:
                robot.enableTorque(k)
        elif event == 'Torque-Off':
            torque = False
            print('torque off')
            for k in dofs:
                if concerned[k]:
                    robot.disableTorque(k)
        elif event == 'Synchro-Off':
            synchro = 0
            print('synchronization off')
        elif event == 'Synchro-On':
            synchro = 1
            print('synchronization on')
        elif event == 'Synchro-Reverse':
            synchro = -1
            print('synchronization reverse')
        elif event == 'Mode-Pose':
            mode = True
            print('record pose')
            record = False
            replay = -1
            window["Stop Recording"].update(text="Next")
        elif event == 'Mode-Movement':
            mode = False
            print('record movement')
            record = False
            replay = -1
            window["Stop Recording"].update(text="Stop")
            if period < 1000:
                beep = False
                window["beep"].update(value=False)
        elif event == "Period":
            period = int(values["Period"])
            if period < 10:
                period = 10
            elif period < 100:
                period = 10*(period//10)
            elif period < 1000:
                period = 100*(period//100)
            else:
                period = 500*(period//500)
            print('period updated to ',period)
            window["Period"].update(value=float(period))
            if period < 1000 and not mode:
                beep = False
                window["beep"].update(value=False)
        elif event == "Save Recording" and values["Save Recording"] != '':
            filename = values["Save Recording"]
            with open(filename, 'w') as f:
                f.write(str(concerned_dofs)+'\n')  
                for r in recorded:
                    f.write(str(r)+'\n')
            window["Save Recording"].update(value='')
            if len(recorded_images) > 0:
                out = cv2.VideoWriter()
                out.open(filename[:-4]+'.avi',cv2.VideoWriter_fourcc('F','F','V','1'),1,recorded_images[0].shape[:2][::-1])
                for image in recorded_images:
                    out.write(image)
                out.release()
            print('saved')
        elif event == "Load Recording" and values["Load Recording"] != '':
            filename = values["Load Recording"]
            recorded = []
            recorded_images = []
            with open(filename, 'r') as f:
                lines = f.readlines()
                concerned_dofs = eval(lines[0])
                for line in lines[1:]:
                    r = eval(line[:-1])
                    recorded.append(r)
                for k in dofs:
                    concerned[k] = False
                for group in groups.keys():
                    concern = False
                    for k in concerned_dofs:
                        if k in groups[group]:
                            concern = True
                            break
                    if concern:
                        for k in groups[group]:
                            concerned[k] = True
                    window['concern-'+group].update(value=concern)
                change_current = False
                for k in concerned_dofs:
                    if k == current:
                        change_current = False
                        break
                    elif synchronized(k) == current:
                        change_current = True
                if change_current:
                    current = synchronized(current)
                    newValue = None
            window["Captured"].update(value=str(len(recorded)))
            window["Load Recording"].update(value='')
            replay = -1
            replaying = False
            print('loaded')        
        elif 'Start Recording' in event:
            print('recording started')
            recorded = []
            recorded_images = []
            concerned_dofs = [ k for k in dofs if concerned[k] ]
            window["Captured"].update(value="0")
            record = True
            replay = -1
            replaying = False
        elif 'Stop Recording' in event:
            if mode:
                print('record next')
                record = True
            else:
                print('recording stopped')
                record = False
            replay = -1
            replaying = False
        elif 'Replay Recording' in event:
            replaying = True
            #print('replaying','one' if mode else 'many','...')
            if not torque:
                torque = True
                window["Torque-On"].update(value=True)
                for k in dofs:
                    robot.enableTorque(k)
        elif event == "beep":
            beep = values["beep"]
            print('beep:',beep)
        elif "concern-" in event:
            if "eye" in event or "Cross" in event:
                concerned[event[8:]] = values[event]
            else:
                for k in groups[event[8:]]:
                    concerned[k] = values[event]
                    if not values[event]:
                        robot.enableTorque(k)
                recorded = []
                recorded_images = []
                concerned_dofs = [ k for k in dofs if concerned[k] ]
                window["Captured"].update(value="0")
                record = False
                replay = -1
                replaying = False

        left_frame, right_frame = cameras.read()
        left_fps, right_fps = cameras.fps()
        left_view = left_frame
        dxy = None
        if left_view is not None and concerned['LeftCross'] and right_view is not None and concerned['RightCross']:
            dxy = image_shift_xy(left_view,right_view)
        if left_view is not None and concerned['LeftCross']:
            left_view = np.copy(left_frame)
            cross(left_view)
        right_view = right_frame
        if right_view is not None and concerned['RightCross']:
            right_view = np.copy(right_frame)
            cross(right_view) 
        if dxy is not None:
            crossAddons(left_view,dxy,-1)
            crossAddons(right_view,dxy,+1)
        if left_frame is not None and left_fps > 1: 
            left_imgbytes = cv2.imencode(".png", cv2.resize(left_view,(320,240)))[1].tobytes()
            window["Left-EYE"].update(data=left_imgbytes)
            window["Left-FPS"].update(value=str(left_fps)+" fps")
            if right_frame is None or right_fps <= 1:
                window["Right-EYE"].update(data=left_imgbytes)
                window["Right-FPS"].update(value="")
        if right_frame is not None and right_fps > 1:
            right_imgbytes = cv2.imencode(".png", cv2.resize(right_view,(320,240)))[1].tobytes()
            window["Right-EYE"].update(data=right_imgbytes)
            window["Right-FPS"].update(value=str(right_fps)+" fps")
        
        t1 = int(time.time()*1000/period)
        if t0 != t1:
            t0 = t1
            for k in dofs:
                position = robot.getAngle(k)
                if k == current:
                    if position == newValue:
                        newValue = None
                if not pressed[k]:
                    window[k].update(value = position)
                    if k == 'head_y':
                        head_z_from, head_z_to = head_z_limits(position)
                        #print('head_z range', head_z_from, head_z_to)
                        window['head_z'].update(range = (head_z_from, head_z_to))
                        
            window['Left-palm'].update(value = robot.getPalmSensorReading("l_hand"))
            window['Right-palm'].update(value = robot.getPalmSensorReading("r_hand"))
            for i in range(2):
                window[controls[0+i*3]].update(value = list(cameras.getZoom())[i])
                window[controls[1+i*3]].update(value = list(cameras.getTilt())[i])
                window[controls[2+i*3]].update(value = list(cameras.getPan())[i])
            if record:
                #print("recording", time.time(),t1)
                recorded.append([values[k] for k in dofs if concerned[k]])
                concerned_frames = [ frame for eye, frame in zip(eyes,[left_frame,right_frame]) if concerned[eye] ]
                if len(concerned_frames) > 0:
                    recorded_images.append(cv2.hconcat(concerned_frames))
                window["Captured"].update(value=str(len(recorded)))
                if beep:
                    chime.warning()
                if mode:
                    record = False
                    print("recorded")
            elif replaying:
                replay += 1
                if replay >= len(recorded):
                    replay = -1
                    replaying = False
                    #print('...replayed many')
                else:
                    positions = { k:position for position, k in zip(recorded[replay],concerned_dofs) }
                    if synchro == 1 or synchro == -1:
                        for k in concerned_dofs:
                            ks = synchronized(k)
                            if ks != k:
                                positions[ks] = positions[k]
                                if synchro == -1:
                                    del positions[k]
                    for k in positions.keys():
                        position = positions[k]
                        robot.setAngle(k,position,defaultSpeed)
                        if not pressed[k]:
                            window[k].update(value = position)
                    if mode:
                        replaying = False
                        #print('...replayed one')
            window["Replayed"].update(value=str(replay),visible=(replay != -1))

except IOError: # serial.serialutil.SerialException
    print('serial line closed')
 
window.close()
del robot
cameras.close()
quit()


