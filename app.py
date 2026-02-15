from flask import Flask, render_template, request, redirect, send_from_directory
from reconstruction import sfm, mvs, meshing
from pathlib import Path

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_from_directory(Path("static/models").resolve(), filename)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file')

    for file in files:
        if file.filename:
            file.save(f'colmap/images/{file.filename}')

    # pipeline de reconstrução
    sfm.run_sfm()
    mvs.run_mvs()
    meshing.generate_mesh()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)