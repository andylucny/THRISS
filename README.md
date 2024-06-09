# THRISS
materials for the Trustworthy Human-Robot Interaction Summer School, WorkShop1 (WS1)

## How to install

We suppose 64-bit operating system, Windows or Linux Ubuntu (or similar POSIX platform).

We suppose Python 3.7, 3.8, 3.9, 3.10 or 3.11 is installed (we have tested on 3.9) and
the paths like C:\Python39 and C:\Python39\Scripts are in PATH

Thus you can open cmd or Terminal and run python or python3 

### Windows

If you have not installed Visual Studio 2019 or newer, 
install the lastest Visual Studio Redistributables from
https://aka.ms/vs/17/release/vc_redist.x64.exe

From https://github.com/andylucny/THRISS.git download zip and unpack it into c:\
so you have this readme in, e.g., C:\THRISS\

start cmd

> \> pip install virtualenv virtualenvwrapper-win <br>
> \> mkvirtualenv thriss

> (thriss)> pip install requests<br>
> (thriss)> pip install PySimpleGUI==4.60.5<br>
> (thriss)> pip install opencv-contrib-python<br>
> (thriss)> pip install chime<br>
> (thriss)> pip install yourdfpy<br>
> (thriss)> pip install "pyglet<2"

> (thriss)> pip install onnxruntime-gpu  (if CUDA is available)

or 

> (thriss)> pip install onnxruntime      (if CUDA is not available)    

> (thriss)> pip install ftfy

### Linux (Ubuntu)

> $ cd ~/ <br>
> $ git clone https://github.com/andylucny/THRISS.git <br>
> $ python3 -m venv virtual/thriss <br>
> $ source virtual/thriss/bin/activate <br>
> (thriss)$ sudo apt-get install python3-tk 

> (thriss)$ pip install requests  <br>
> (thriss)$ pip install PySimpleGUI==4.60.5 <br>
> (thriss)$ pip install opencv-contrib-python <br>
> (thriss)$ pip install chime <br>
> (thriss)$ pip install "pyglet<2" <br>
> (thriss)$ pip install trimesh==3.11.2 <br>
> (thriss)$ pip install yourdfpy

> (thriss)$ pip install onnxruntime-gpu  (if CUDA is available) 

or
 
> (thriss)$ pip install onnxruntime      (if CUDA is not available) 

> (thriss)$ pip install ftfy

## How to use

### Windows

> \> workon thriss <br>
> (thriss)> python my.py

### Linux (Ubuntu)

> $ cd ~/ <br>
> $ source virtual/thriss/bin/activate <br>
> $ cd thriss/... <br>
> (thriss)$ python3 my.py 

