import os
import time
from nicomover import setAngle, getAngle, enableTorque, disableTorque, park, release
from nicomover import current_posture, move_to_posture, load_movement, play_movement

def quit():
    release()
    os._exit(0)

posture = current_posture()
dofs = list(posture.keys())
print(dofs)

enableTorque(dofs)

setAngle('l_elbow_y',60,0.04) 
time.sleep(2)
setAngle('l_elbow_y',85,0.04)
time.sleep(2)

#park()
#disableTorque(dofs)

postures = load_movement('movement.txt')

#move_to_posture(postures[0])
#time.sleep(2)
#play_movement(postures)

# len(postures) == 7
durations = [2, 1,  0.58, 0.9, 0.5, 0.8, 1] # [s]
play_movement(postures, durations)

# quit()