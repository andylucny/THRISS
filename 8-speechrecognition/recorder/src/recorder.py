#how to install:
#pip install pipwin
#pipwin install pyaudio # wait on hang ...
#pip install SpeechRecognition

import tkinter as tk
import threading
import time
import speech_recognition as sr
from agentspace import Space
from sender_client import SenderAgent

class App():
    def __init__(self, master):
        self.r = sr.Recognizer()
        self.isrecording = False
        self.buttonText = tk.StringVar()
        self.buttonText.set('Press to record')
        self.button = tk.Button(main, textvariable=self.buttonText)
        self.button.bind("<Button-1>", self.startrecording)
        self.button.bind("<ButtonRelease-1>", self.stoprecording)
        self.button.pack()
        self.txt = tk.Text(main, height = 1, width = 25, bg = "light yellow")
        self.txt.pack()
        self.button2 = tk.Button(main, text="Connect")
        self.button2.bind("<Button-1>", self.reconnect)
        self.button2.pack()

    def startrecording(self, event):
        self.isrecording = True
        self.buttonText.set('Recording...')
        t = threading.Thread(target=self._record)
        t.start()

    def stoprecording(self, event):
        self.isrecording = False
        self.buttonText.set('Press to record')
        
    def _record(self):
        self.txt.delete(0.0,tk.END)
        while self.isrecording:
            with sr.Microphone() as source: 
                #self.r.adjust_for_ambient_noise(source) 
                audio = self.r.listen(source)
                try:
                    text = self.r.recognize_google(audio,language="en")
                    self.txt.insert(tk.INSERT,text)
                    Space.write('recognized',text)
                    #print(text)
                except:
                    self.txt.insert(tk.INSERT,'???')
                    #print('???')

    def reconnect(self, event):
        global sender
        sender.stop()
        time.sleep(0.5)
        createSender()
    
def createSender():
    global sender
    sender = SenderAgent('localhost',7171,'recognized')

if __name__ == "__main__":
    createSender()
    main = tk.Tk()
    app = App(main)
    main.mainloop()
