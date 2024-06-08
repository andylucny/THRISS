import time
from agentspace import space

space["a"] = 1
print(space["a"]) # 1

space(validity=1.5)["a"] = 2 # validity is measured in [s]
print(space["a"]) # 2
time.sleep(2)
print(space["a"]) # None

print(space(default=-1)["a"]) # -1

space(priority=2)["a"] = 3
space(priority=1)["a"] = 4
space["a"] = 5 # default priority is 1
print(space["a"]) # 3

space(validity=1, priority=3)["a"] = 6
print(space["a"]) # 6
time.sleep(1.5)
print(space["a"]) # None

space["a"] = 7
space["a"] = None # delete
