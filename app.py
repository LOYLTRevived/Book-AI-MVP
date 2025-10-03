from email.mime import message
import os
import sys
import subprocess
from flask import Flask, flash, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecret"
UPLOAD_FOLDER = os.path.join('data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_uploaded_file(filepath):
    # 1. Ingest and chunk the file
    ingest_cmd = [sys.executable, "ingest.py", filepath]
    ingest_result = subprocess.run(ingest_cmd, capture_output=True, text=True)
    print("Ingest Output:", ingest_result.stdout)
    if ingest_result.returncode != 0:
        print("Ingest error:", ingest_result.stderr)
        return False, "Ingest failed"
    
    # 2. Extract claims from the chunked file
    # Find the generated chunk file (assuming naming convention)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    chunk_file = os.path.join("data", f"{base_name}_chunks.json")
    if not os.path.exists(chunk_file):
        return False, "Chunk file not found after ingest"
    
    extract_cmd = [sys.executable, "extract_claims.py", chunk_file]
    extract_result = subprocess.run(extract_cmd, capture_output=True, text=True)
    print("Extract Output:", extract_result.stdout)
    if extract_result.returncode != 0:
        print("Extract error:", extract_result.stderr)
        return False, "Extract failed"

    return True, "Processing successful"

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        topic = request.form.get("topic")
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            print(f"File received:", file)
            print(f"Topic:", topic)
            success, message = process_uploaded_file(filepath)
            if success:
                flash(message, "success")
            else:
                flash(message, "error")  
            return redirect(url_for("upload"))
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)