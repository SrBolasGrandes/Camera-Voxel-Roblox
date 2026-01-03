from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import cv2, threading, time, requests, numpy as np

app = Flask(__name__)
CORS(app)

GRID = 96
FPS = 20
MODE = "color"
TIMEOUT = 2

GITHUB_USER = "SrBolasGrandes"
GITHUB_REPO = "Camera-Voxel-Roblox"
VIDEOS_PATH = "videos"
BRANCH = "main"

FALLBACK_URL = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

frame_data = {"data": []}
last_frame_time = 0
lock = threading.Lock()
video_cap = None
paused = False

def img_to_pixels(img):
	img = cv2.resize(img, (GRID, GRID))
	out = []
	for y in range(GRID):
		for x in range(GRID):
			b,g,r = img[y,x]
			out.append([int(r),int(g),int(b)])
	return out

def load_fallback():
	r = requests.get(FALLBACK_URL)
	img = np.frombuffer(r.content, np.uint8)
	img = cv2.imdecode(img, cv2.IMREAD_COLOR)
	return img_to_pixels(img)

FALLBACK = load_fallback()

def watchdog():
	while True:
		time.sleep(0.2)
		with lock:
			if time.time() - last_frame_time > TIMEOUT:
				frame_data["data"] = FALLBACK

threading.Thread(target=watchdog, daemon=True).start()

def process(frame):
	global MODE
	if MODE == "bw":
		g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
	return img_to_pixels(frame)

def video_loop():
	global video_cap, paused, last_frame_time
	while True:
		time.sleep(1/FPS)
		if video_cap and not paused:
			ok, frame = video_cap.read()
			if not ok:
				video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
				continue
			with lock:
				frame_data["data"] = process(frame)
				last_frame_time = time.time()

threading.Thread(target=video_loop, daemon=True).start()

@app.route("/")
def index():
	return "Camera Voxel Server OK"

@app.route("/camera")
def camera():
	return render_template("camera.html")

@app.route("/video")
def video():
	return render_template("video.html")

@app.route("/pushFrame", methods=["POST"])
def push():
	global last_frame_time
	img = np.frombuffer(request.data, np.uint8)
	frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
	with lock:
		frame_data["data"] = process(frame)
		last_frame_time = time.time()
	return "ok"

@app.route("/cameraGet")
def get():
	with lock:
		return jsonify(frame_data)

@app.route("/videosList")
def list_videos():
	url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{VIDEOS_PATH}?ref={BRANCH}"
	r = requests.get(url).json()
	out = []
	for f in r:
		if f["name"].lower().endswith((".mp4",".webm",".mov",".avi")):
			out.append({"name":f["name"],"url":f["download_url"]})
	return jsonify(out)

@app.route("/playVideo", methods=["POST"])
def play_video():
	global video_cap, paused
	video_cap = cv2.VideoCapture(request.json["url"])
	paused = False
	return "ok"

@app.route("/pauseVideo", methods=["POST"])
def pause():
	global paused
	paused = True
	return "ok"

@app.route("/resumeVideo", methods=["POST"])
def resume():
	global paused
	paused = False
	return "ok"

@app.route("/setMode", methods=["POST"])
def set_mode():
	global MODE
	MODE = request.json["mode"]
	return "ok"

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=10000)
