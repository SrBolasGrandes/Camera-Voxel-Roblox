from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io

app = Flask(__name__)
CORS(app)

GRID = 96
last_frame = None

@app.route("/")
def home():
    return render_template("camera.html")

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame

    mode = request.json.get("mode", "color")
    raw = base64.b64decode(request.json["image"])

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((GRID, GRID), Image.BILINEAR)

    pixels = list(img.getdata())

    if mode == "bw":
        bw_pixels = []
        for r, g, b in pixels:
            l = int((r * 0.299) + (g * 0.587) + (b * 0.114))
            bw_pixels.append((l, l, l))
        last_frame = bw_pixels
    else:
        last_frame = pixels

    return jsonify(ok=True)

@app.route("/cameraGet")
def camera_get():
    if last_frame is None:
        return jsonify(ready=False)

    return jsonify(
        ready=True,
        size=GRID,
        data=last_frame
    )

if __name__ == "__main__":
    app.run()
