from modules import *

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import time
import os
import glob
from threading import Thread
import signal
import random
import traceback
import requests
import re

videoDuration = 5
countdownDuration = 10
storageAddress = "http://10.42.0.2"
subDir = "/PRIVATE/M4ROOT/SUB"

bleAddress = "00:9D:6B:B9:06:16"
camera = SonyBLE(bleAddress)

class Status:
    IDLE = 0
    INSTRUCTIONS = 1
    COUNTDOWN = 2
    RECORDING = 3
    DOWNLOADING = 4
    DECISION_KEEP = 5
    DECISION_PRINT = 6
    ERROR = 7

app = Flask(__name__)

status = Status.IDLE
timeRef = 0
lastPreviewFinish = 30
randomMapping = {}

@app.route("/", methods = ["GET"])
def interface():
    return render_template('index.html')

@app.route("/status", methods = ["GET"])
def interfaceStatus():
    response = {}
    response["status"] = status
    response["timeRef"] = timeRef
    response["duration"] = videoDuration
    response["finish"] = lastPreviewFinish + 5
    return jsonify(response)

@app.route("/control", methods = ["GET"])
def interfaceControl():
    if "cmd" in request.args:
        if request.args["cmd"] == "ok":
            ok()
        elif request.args["cmd"] == "abort":
            abort()
    return ""

@app.route("/preview", methods = ["GET"])
def filePreview():
    if os.path.isfile("preview.mp4"):
        return send_file("preview.mp4", mimetype="video/mp4")
    return ""

@app.route("/previewGB", methods = ["GET"])
def fileGBPreview():
    if os.path.isfile("gb.mp4"):
        return send_file("gb.mp4", mimetype="video/mp4")
    return ""
    
@app.route("/printpreview", methods = ["GET"])
def printPreview():
    if os.path.isfile("print.png"):
        return send_file("print.png", mimetype="image/png")
    return ""

def getRandomFilename(i):
    available = []
    for filename in sorted(glob.glob("../data/cam/*.mp4")):
        available.append(filename)
    if len(available) == 0:
        return ""
    if not i in randomMapping:
        randomMapping[i] = random.randrange(len(available))
    return available[randomMapping[i]]

@app.route("/random", methods = ["GET"])
def fileRandomVideo():
    if "i" in request.args:
        i = int(request.args["i"])
        filename = getRandomFilename(i)
        if len(filename) == 0:
            return ""
        return send_file(filename, mimetype="video/mp4")
    return ""

@app.route("/randomGB", methods = ["GET"])
def fileRandomGBVideo():
    if "i" in request.args:
        i = int(request.args["i"])
        filename = getRandomFilename(i)
        if len(filename) == 0:
            return ""
        print(filename)
        gbfilename = filename[:8] + "gb" + filename[11:] #Quick and dirty replacement of .../cam/... with .../gb/...
        print(gbfilename)
        if os.path.isfile(gbfilename):
            return send_file(gbfilename, mimetype="video/mp4")
    return ""

def ok():
    global status
    if status == Status.IDLE:
        status = Status.INSTRUCTIONS
    elif status == Status.INSTRUCTIONS:
        Thread(target = execute).start()
    elif status == Status.DECISION_KEEP:
        filename = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        if os.path.isfile("preview.mp4"):
            os.rename("preview.mp4", "../data/cam/" + filename + ".mp4" )
        if os.path.isfile("gb.mjpeg"):
            os.rename("gb.mjpeg", "../data/gb/" + filename + ".mjpeg" )
        if os.path.isfile("gb.mp4"):
            os.rename("gb.mp4", "../data/gb/" + filename + ".mp4" )
        status = Status.DECISION_PRINT
    elif status == Status.DECISION_PRINT:
        try:
            if os.path.isfile("print.png"):
                filename = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
                os.rename("print.png", "../data/print/" + filename + ".png" )
                with GBPrinter("/dev/ttyACM0", 115200) as gbp:
                    gbp.printImageFromFile("../data/print/" + filename + ".png", 0.5)
                
            status = Status.IDLE
        except:
            traceback.print_exc()
            tryRecover()


def abort():
    global status
    if status == Status.DECISION_KEEP: #Pressing the red button on the keep decision screen leads to...
        status = Status.DECISION_PRINT #...the print decision screen
    else:                              #In all other cases...
        status = Status.IDLE           #the red button aborts the entire sequence.

def execute():
    global status, timeRef, lastPreviewFinish
    try:
        timeRef = time.time() + countdownDuration
        status = Status.COUNTDOWN

        filesBefore = getStorageState()

        while time.time()-timeRef < 0.0:
            if status == Status.IDLE:
                return
        print("Start video recording")
        startRecording()

        status = Status.RECORDING

        print("Waiting for recording")
        while time.time()-timeRef < videoDuration:
            if status == Status.IDLE:
                stopRecording()
                return

        print("Stopping video recording")
        stopRecording()

        if status == Status.IDLE:
            return

        status = Status.DOWNLOADING

        for i in range(3):
            time.sleep(3)

            if status == Status.IDLE:
                return
            print(str(time.time()-timeRef) + " Downloading...")

            filesAfter = getStorageState()
            newFiles = list(set(filesAfter)-set(filesBefore))
            if len(newFiles) > 0:
                newFile = newFiles[0]
                break

        downloadRecording(subDir + "/" + newFile)

        os.system("ffmpeg -i gb.mjpeg -s 160x144 -y gb.mp4")

        os.system("ffmpeg -i gb.mjpeg -i filmtransport.png -frames 1 -filter_complex \"[0:v]select=not(mod(n-15\,60)),scale=160:144,crop=128:112:16:16,tile=1x3:padding=6,pad=width=160:height=368:x=16:y=14[tiles];[tiles][1:v]overlay\" -update 1 -y print.png")

        if status == Status.IDLE:
            return
        
        print(str(time.time()-timeRef) + " Done.")
        lastPreviewFinish = time.time()-timeRef
        if status == Status.IDLE:
            return
        status = Status.DECISION_KEEP
    except:
        traceback.print_exc()
        tryRecover()

def tryRecover():
    global status
    status = Status.ERROR
    happy = False
    while not happy:
        try:
            print("Closing old connections.")
            disconnectCamera()

            time.sleep(10)

            print("Connecting...")
            connectCamera()
            getStorageState()
            #TODO Test Printer state and show actual error on screen
            happy = True
        except:
            traceback.print_exc()
            continue

    print("Ready. Hopefully...")
    status = Status.IDLE


def connectCamera():
    camera.connect()

def disconnectCamera():
    camera.disconnect()

def getStorageState():
    response = requests.get(storageAddress + "/command.cgi?op=100&DIR=" + subDir)
    filenames = []
    for line in response.text.splitlines():
        filename =  re.search(r".*?,(.*?),.*?,.*?,.*?,.*?", line)
        if filename != None:
            filenames.append(filename.group(1))
    return filenames

def startRecording():
    camera.triggerRecording()
    videoCam.recordVideo(videoDuration*30, "gb.mjpeg")

def stopRecording():
    while camera.isRecording():
        camera.triggerRecording()
        time.sleep(1)

def downloadRecording(url):
    response = requests.get(storageAddress + url)
    with open("preview.mp4", "wb") as file:
        file.write(response.content)

if __name__ == "__main__":
    print("Connecting...")
    connectCamera()
    print("Ready.")
    from waitress import serve
    while True:
        try:
            serve(app, host="0.0.0.0", port=8080, threads=4)
        except:
            pass
    print("Exiting...")
    disconnectCamera()

