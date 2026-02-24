from flask import Flask, render_template, request, redirect, send_from_directory
from reconstruction import sfm, mvs, meshing, preprocessing
from pathlib import Path
import shutil

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_from_directory(Path("static/models").resolve(), filename)


@app.route("/upload", methods=["POST"])
def upload():

    uploaded_files = request.files.getlist("file")
    strategy = "sem_fundo"

    original_dir = Path("colmap/images")
    processed_dir = Path("colmap/images_processed")

    # limpa imagens processadas anteriores
    if processed_dir.exists():
        shutil.rmtree(processed_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    original_dir.mkdir(parents=True, exist_ok=True)

    # aplica o pré-processamento em cada imagem e salva na pasta de entrada do SfM
    for file in uploaded_files:
        if file.filename:
            original_path = original_dir / file.filename
            file.save(original_path)

            preprocessing.preprocess_image(
                input_path=str(original_path),
                output_base_dir=str(processed_dir),
                strategy=strategy
            )

    sfm_input_dir = processed_dir / strategy

    sfm.run_sfm(str(sfm_input_dir))
    mvs.run_mvs(str(sfm_input_dir))
    meshing.generate_mesh()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)