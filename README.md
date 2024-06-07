# THRISS
materials for the Trustworthy Human-Robot Interaction Summer School, WorkShop1 (WS1)

## How to install

We suppose 64-bit operating system, Windows or Linux Ubuntu (or similar POSIX platform).

We suppose Python 3.7, 3.8, 3.9, 3.10 or 3.11 is installed (tested on 3.9)

### Windows

From https://github.com/andylucny/THRISS.git download zip and unpack it into c:\
so you have this readme in C:\THRISS\

start cmd

> pip install virtualenv virtualenvwrapper-win 
> mkvirtualenv thriss 

(thriss)> pip install requests
(thriss)> pip install PySimpleGUI==4.60.5
(thriss)> pip install opencv-contrib-python
(thriss)> pip install chime
(thriss)> pip install yourdfpy
(thriss)> pip install "pyglet<2"

(thriss)> pip install onnxruntime-gpu  (if CUDA is available)
or 
(thriss)> pip install onnxruntime      (if CUDA is not available)    

(thriss)> pip install ftfy

### Linux (Ubuntu)

$ cd ~/
$ git clone https://github.com/andylucny/THRISS.git
$ python3 -m venv virtual/thriss
$ source virtual/thriss/bin/activate
(thriss)$ sudo apt-get install python3-tk

(thriss)$ pip install requests
(thriss)$ pip install PySimpleGUI==4.60.5
(thriss)$ pip install opencv-contrib-python
(thriss)$ pip install chime
(thriss)$ pip install "pyglet<2"
(thriss)$ pip install trimesh==3.11.2 
(thriss)$ pip install yourdfpy

(thriss)$ pip install onnxruntime-gpu  (if CUDA is available)
or 
(thriss)$ pip install onnxruntime      (if CUDA is not available)    

(thriss)$ pip install ftfy

## How to use

### Windows

> workon thriss 
(thriss)> python my.py

### Linux (Ubuntu)

$ cd ~/
$ source virtual/thriss/bin/activate
$ cd thriss/...
(thriss)$ python3 my.py

