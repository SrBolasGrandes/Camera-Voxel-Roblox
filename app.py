from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, os, requests

app = Flask(__name__)
CORS(app)

GRID = 96
TIMEOUT = 3

last_frame = None
last_time = 0

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

FALLBACK = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

def load_fallback():
    global last_frame
    r = requests.get(FALLBACK)
    img = Image.open(io.BytesIO(r.content)).convert("RGB").resize((GRID,GRID))
    last_frame = list(img.getdata())

@app.route("/")
def cam():
    return render_template("camera.html")

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["video"]
    f.save(os.path.join(UPLOAD_DIR,"video.mp4"))
    return "ok"

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame,last_time

    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB").resize((GRID,GRID))
    last_frame = list(img.getdata())
    last_time = time.time()

    return jsonify(ok=True)

@app.route("/cameraGet")
def get():
    if last_frame is None or time.time()-last_time>TIMEOUT:
        load_fallback()

    return jsonify(
        ready=True,
        size=GRID,
        data=last_frame
    )

if __name__ == "__main__":
    app.run()
