from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, requests

app = Flask(__name__)
CORS(app)

GRID = 96
FPS = 20
TIMEOUT = 3

camera_frame = None
camera_time = 0

anime_frame = None
anime_time = 0

GITHUB_USER = "SrBolasGrandes"
REPO = "Camera-Voxel-Roblox"
VIDEOS_PATH = "videos"

ANIME_STREAM = "https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/5f12136385bccc00070142ed/master.m3u8"

FALLBACK_IMG = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

def img_to_pixels(img):
    img = img.resize((GRID, GRID))
    return list(img.getdata())

def load_fallback():
    r = requests.get(FALLBACK_IMG)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    return img_to_pixels(img)

@app.route("/")
def camera_page():
    return render_template("camera.html")

@app.route("/video")
def video_page():
    return render_template("video.html")

@app.route("/anime")
def anime_page():
    return render_template("anime.html")

@app.route("/videosList")
def videos_list():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{VIDEOS_PATH}"
    r = requests.get(url)
    if r.status_code != 200:
        return jsonify([])

    out = []
    for f in r.json():
        if f["name"].lower().endswith(".mp4"):
            out.append({
                "name": f["name"],
                "url": f["download_url"]
            })
    return jsonify(out)

@app.route("/camera", methods=["POST"])
def camera():
    global camera_frame, camera_time
    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    camera_frame = img_to_pixels(img)
    camera_time = time.time()
    return jsonify(ok=True)

@app.route("/animeFrame", methods=["POST"])
def anime_frame_post():
    global anime_frame, anime_time
    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    anime_frame = img_to_pixels(img)
    anime_time = time.time()
    return jsonify(ok=True)

@app.route("/cameraGet")
def camera_get():
    if camera_frame is None or time.time() - camera_time > TIMEOUT:
        return jsonify(ready=True, size=GRID, data=load_fallback())
    return jsonify(ready=True, size=GRID, data=camera_frame)

@app.route("/animeGet")
def anime_get():
    if anime_frame is None or time.time() - anime_time > TIMEOUT:
        return jsonify(ready=True, size=GRID, data=load_fallback())
    return jsonify(ready=True, size=GRID, data=anime_frame)

if __name__ == "__main__":
    app.run()
