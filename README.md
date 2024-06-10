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

> (thriss)> pip install ftfy<br>
> (thriss)> pip install regex<br>
> (thriss)> pip install pyttsx3

if you like launching the recorder application from sources (instead of binaries), install also:

> (thriss)> pip install pyaudio<br>
> (thriss)> pip install SpeechRecognition

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

> (thriss)$ pip install ftfy<br>
> (thriss)$ pip install regex

> (thriss)$ sudo apt install espeak<br>
> (thriss)$ pip install pyttsx3

> (thriss)$ sudo apt install portaudio19-dev python3-pyaudio<br>
> (thriss)$ pip install pyaudio<br>
> (thriss)$ pip install SpeechRecognition

## How to use

### Windows

> \> workon thriss <br>
> (thriss)> python my.py

### Linux (Ubuntu)

> $ cd ~/ <br>
> $ source virtual/thriss/bin/activate <br>
> $ cd thriss/... <br>
> (thriss)$ python3 my.py 

## Tutorial

Your task is to design an interaction between you and the NICO robot and try it with the simulator. Once you've designed this interaction, you'll be satisfied to record it in an impressive video with the real robot. This video is evaluated and ranked; you can submit more versions. 

Let's start by familiarizing ourselves with the components available to you. We'll do this in eight manageable steps:

### 1-nicogui

Learn the NICO robot's movement capabilities. NICO has 22 degrees of freedom: 2 in the head, 4 in the arm, 2 in the wrist, and 4 in the fingers. Launch: "python nicogui.py" and choose a posture, like "pointing up." Use NICOgui sliders to set it up. Record the pose by the button "Start"; follow the number of frames displayed by "Capture." Record a few other postures using the button "Next." Then, replay the recorded data by clicking Replay. Change "Pose" to "Movement," set up a suitable period, and Replay again with one click. Finally, save the movement on the hard disk by "Save."

### 2-nicomover

Learn how you can control NICO's movement using your Python program. Launch: "python -i main.py" - the interactive mode. Look into the main.py to get an idea of what commands to type. Replay the movement recorded in the NICOgui. Finally, exit by ">>> quit()"

### 3-camera

Run "python camera.py" and move in front of the camera. Save a few images with different objects shown to the camera by pressing the key "s" (before the key reacts, you must click into the image window to make it active). Finally, press Esc.

### 4-integration

Even a simple human-robot interaction system must run many processes in parallel and encounter troubles integrating many parallel modules. We use a blackboard architecture that encapsulates these modules into so-called agents and allows them to communicate via the backboard. The backboard (called here "space") is an extended Python dictionary. Besides the standard operations "space[key] = value" or "value = space[key]," it also supports time validity: "space(validity=0.5)[key] = value" - the value is valid for 0.5s and then expires, and priority: "space(priority=2)[key] = value" that can override only values written with priority two or lower (the default priority is 1). Run "python -i tryspace.py" and exit by quit(). Run "python tryagent.py." It is tricky to stop a system running more parallel threads: use ctrl-c on Linux or ctrl-break on Windows. (Some notebooks have no break key; use ctrl-alt-b.)

### 5-dino

DINO is a foundation model that turns images into attention maps. Run "python dino.py" to see how it works. Replace the processed image with one of your images taken by "camera.py." Finally, launch "trydino.py" and test how the attention map reacts to an object moving in front of the camera. Notice that DINO provides six attention maps; map 2 is the best for close objects. Look inside the program: each attention map is thresholded to a binary mask, and the average of the binary mask pixel's coordinates indicates the point of interest. Thus, we get six points from each frame and employ one of them. We use Kalman filtering to avoid too much variation of the points. Notice also how we use the blackboard to prevent overwhelming the DINO model with images provided by the camera at a higher rate than the model can process.

### 6-clip

CLIP is a foundation model that provides analogical embedding (features) for texts and images. In other words, it turns pictures and their captions into similar vectors. As a result, the scalar product of the image and text embeddings is maximal when the text describes the image. Launch "python clip.py" and understand the results. You can modify the program to print out the dimension of the CLIP features. This number indicates how many ways two images or texts can differ. It is low to be perfect, but CLIP is beneficial when distinguishing a few image categories. Run "tryclip.py" to test this ability. First, use the key "k" to define the category 0 (background). Then, present an object to the camera and press the key "k" to create category 1. Create several categories this way, then follow how CLIP reacts to changing objects in front of the camera.

### 7-speechsynthesis

Check that speech synthesis works by "python -i speak.py." Let the machine tell something else. Run "python -i tryspeak.py" and notice how these two services differ: the first is blocking while the second is non-blocking.

### 8-speechrecognition

For speech recognition, we use a cloud solution. We call it Google Cloud, located on the other side of our planet, but the Internet allows us to call it comfortably. We have developed an application that records voice, sends it to the cloud, receives text, and routes it to your program via TCP. Thus, the speech recognition is represented in your system by a TCP receiver - run "python tryrecorder.py" - and the external application "recorder" needs to be run in parallel. The application is supplied both in sources and binaries (for Windows). On Windows, run recorder.bat. On Linux, you to run it from sources: "sudo chmod 0777 recorder.sh" and "./recorder.sh". Push the button "Press" and keep it while speaking to the microphone. Then, the text appears (after several seconds). The tryrecorder.py program should also receive the text. (Ignore the ALSA errors and warnings on Linux.) 

### project

Finally, we can combine all the ingredients into a complex system. Design a human-robot interaction that you can develop from the available sources. Then, modify the bottom part of the main.py (the Control Agent) to implement it. The provided system implements an interaction in which the robot shakes its head and says yes or no to questions of the form "Is this XY?" as follows. The CameraAgent takes pictures from the camera and puts them on the blackboard as "RobotEye." The PerceptionAgent applied DINO and CLIP models on it and outputs "dinoPoints" and "clipFeatures." The LookAroundAgent employs the points for moving NICO's head, being curious, and following close objects. It can be stopped (i.e., for shaking the head) by "dontLook," which is True or False. The SpeakerAgent serializes commands for speaking; thus, you can call the non-blocking "self.speak(text)". (If you like to wait, call "time.sleep(seconds)." The ReceiverAgent listens to port 7171, where the recorder application transmits the text recognized from speech. Finally, the ControlAgent receives two kinds of data: the CLIP features (and corresponding images) and texts from speech recognition. It is up to you to manage how to use them. (If this task is too difficult, create just your version of mykeys.npy - e.g., by tryclip.py, and record your video with the head-shaking interaction.)
