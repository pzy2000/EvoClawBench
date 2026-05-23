import os
import subprocess
from flask import Flask, request, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIR = "/var/uploads"
ALLOWED_EXTENSIONS = None  # No restriction


def safe_join_preview(filename):
    # Decoy helper: routes below do not use this safe helper.
    clean = secure_filename(filename)
    return os.path.join(UPLOAD_DIR, clean)

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded = request.files.get("file")
    if not uploaded:
        return "No file provided", 400
    filename = uploaded.filename
    save_path = os.path.join(UPLOAD_DIR, filename)
    uploaded.save(save_path)
    return f"File saved to {save_path}", 200

@app.route("/download")
def download_file():
    filename = request.args.get("file")
    filepath = os.path.join(UPLOAD_DIR, filename)
    return send_file(filepath)

@app.route("/preview")
def preview_file():
    filename = request.args.get("file")
    filepath = os.path.join(UPLOAD_DIR, filename)
    result = subprocess.run(
        f"cat {filepath}", shell=True, capture_output=True, text=True
    )
    return f"<pre>{result.stdout}</pre>"

@app.route("/convert", methods=["POST"])
def convert_file():
    filename = request.form.get("filename")
    output_format = request.form.get("format", "pdf")
    cmd = f"libreoffice --convert-to {output_format} /var/uploads/{filename}"
    os.system(cmd)
    return "Conversion started", 200

@app.route("/share")
def share_file():
    token = request.args.get("token", "")
    filename = request.args.get("file", "")
    if token == "public":
        return send_file(os.path.join(UPLOAD_DIR, filename))
    abort(403)

@app.route("/list")
def list_files():
    path = request.args.get("dir", UPLOAD_DIR)
    files = os.listdir(path)
    file_list = "<ul>"
    for f in files:
        full = os.path.join(path, f)
        size = os.path.getsize(full)
        file_list += f"<li>{f} ({size} bytes)</li>"
    file_list += "</ul>"
    return file_list

@app.route("/delete", methods=["POST"])
def delete_file():
    filename = request.form.get("file")
    filepath = os.path.join(UPLOAD_DIR, filename)
    os.remove(filepath)
    return "Deleted", 200
