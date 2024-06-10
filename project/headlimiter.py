# We solved the overload problem, which appeared when NICO reached a farther spot, 
# by adding the lead counterweights to NICO's shoulders. As a result, NICO's head 
# can collide with the counterweights. So, we have to apply the head movement limiter, 
# which allows a dynamic range of head movement from the left to the right according 
# to the current head position from top to bottom.

import numpy as np
import cv2 as cv
import time

headLimits = [ # head_y .. head_z_limit
    [-50,  2],
    [-46, 13],
    [-40, 27],
    [-35, 30],
    [-30, 33],
    [-25, 40],
    [-20, 51],
    [-16, 89],
]

hx, hy = np.array(headLimits).T
fit = np.polyfit(hx, hy, 6)
poly = np.poly1d(fit)

def head_z_limits(head_y):
    if head_y > -15:
        return -90, 90
    limit = poly(head_y)
    limit = round(limit)
    limit = min(90,limit)
    return -limit, limit

if __name__ == "__main__":
    _, hhy = head_z_limits(hx)
    print(np.array([hhy,hy]).T)

