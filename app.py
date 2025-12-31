from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance
import base64, io

app = Flask(__name__)
last_frame = None
GRID = 32

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame

    img_data = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(img_data)).convert("RGB")

    img = img.resize((GRID, GRID))
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.2)

    gray = img.convert("L")
    pixels = list(gray.getdata())

    fixed = []
    for v in pixels:
        v = int((v / 255) ** 0.8 * 255)
        if v < 20:
            v = 20
        fixed.append(v)

    last_frame = fixed
    return jsonify({"ok": True})

@app.route("/cameraGet", methods=["GET"])
def camera_get():
    if last_frame is None:
        return jsonify({"ready": False})

    data = []
    for v in last_frame:
        depth = int((255 - v) / 255 * 20)
        data.append([v, depth])

    return jsonify({"ready": True, "data": data})
