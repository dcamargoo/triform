from flask import Flask, render_template, request, redirect, send_from_directory
from reconstruction import sfm, mvs, meshing, preprocessing
from pathlib import Path
import shutil

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

    ORIGINAL_DIR = Path("colmap/images")               # apenas originais
    PROCESSED_DIR = Path("colmap/images_processed")    # apenas tratadas

    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # limpar imagens processadas antigas
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for file in files:
        if file.filename:
            original_path = ORIGINAL_DIR / file.filename

            # salvar ORIGINAL
            file.save(original_path)

            # gerar versões processadas em subpastas
            preprocessing.preprocess_image(
                input_path=str(original_path),
                output_base_dir=str(PROCESSED_DIR)
            )

    # agora o SfM usa APENAS images_processed
    sfm.run_sfm()
    mvs.run_mvs()
    meshing.generate_mesh()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)