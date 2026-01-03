from flask import Flask, render_template, request, jsonify
from PIL import Image
import cv2
import os
import io
import time

app = Flask(__name__)

FRAME = []
READY = False

SIZE = 96
VIDEO_CAP = None

def img_to_pixels(img):
    img = img.resize((SIZE, SIZE)).convert("RGB")
    data = []
    for y in range(SIZE):
        for x in range(SIZE):
            r,g,b = img.getpixel((x,y))
            data.append([r,g,b])
    return data

@app.route("/cameraGet")
def camera_get():
    return jsonify({"ready": READY, "data": FRAME})

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route("/cameraSend", methods=["POST"])
def camera_send():
    global FRAME, READY
    img = Image.open(io.BytesIO(request.data))
    FRAME = img_to_pixels(img)
    READY = True
    return "ok"

@app.route("/foto")
def foto():
    return render_template("foto.html")

@app.route("/fotoSend", methods=["POST"])
def foto_send():
    global FRAME, READY
    img = Image.open(request.files["image"].stream)
    FRAME = img_to_pixels(img)
    READY = True
    return "ok"

@app.route("/video")
def video():
    files = [f for f in os.listdir("videos") if f.endswith(".mp4")]
    return render_template("video.html", videos=files)

@app.route("/videoPlay", methods=["POST"])
def video_play():
    global VIDEO_CAP
    VIDEO_CAP = cv2.VideoCapture("videos/" + request.json["name"])
    return "ok"

@app.route("/videoFrame")
def video_frame():
    global FRAME, READY, VIDEO_CAP
    if VIDEO_CAP:
        ok, frame = VIDEO_CAP.read()
        if ok:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            FRAME = img_to_pixels(img)
            READY = True
    return "ok"

if __name__ == "__main__":
    app.run()
