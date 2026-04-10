from flask import Flask, render_template, request, send_file, jsonify
from reconstruction import preprocessing, sfm, mvs, meshing, export
from pathlib import Path
import shutil
import threading

app = Flask(__name__)

# variáveis globais de estado
current_stage = "idle"
cancel_flag = False
pipeline_thread = None
current_error = ""
VALID_STRATEGIES = {"com_fundo", "sem_fundo"}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_file(Path("static/models") / filename)


@app.route("/upload", methods=["POST"])
def upload():
    global current_stage, cancel_flag, pipeline_thread, current_error

    uploaded_files = request.files.getlist("file")

    print("uploaded_files:", uploaded_files)
    print("quantidade:", len(uploaded_files))
    for i, file in enumerate(uploaded_files):
        print(f"arquivo {i}: filename={repr(getattr(file, 'filename', None))}")

    try:
        depth = int(request.form.get("depth", 9))
    except:
        depth = 9

    depth = max(7, min(12, depth))
    strategy = request.form.get("strategy", "com_fundo")

    if strategy not in VALID_STRATEGIES:
        strategy = "com_fundo"

    invert_normals = request.form.get("invertNormals", "false") == "true"

    original_dir = Path("colmap/images")
    processed_dir = Path("colmap/images_processed")

    if original_dir.exists():
        shutil.rmtree(original_dir)

    if processed_dir.exists():
        shutil.rmtree(processed_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    original_dir.mkdir(parents=True, exist_ok=True)

    valid_files = []
    for file in uploaded_files:
        filename = getattr(file, "filename", "").strip()
        if filename:
            valid_files.append(file)

    if not valid_files:
        return jsonify({
            "status": "error",
            "error": "Nenhuma imagem válida foi enviada."
        }), 400

    saved_filenames = []

    for file in valid_files:
        filename = file.filename.strip()
        original_path = original_dir / filename
        file.save(original_path)
        saved_filenames.append(filename)

    cancel_flag = False
    current_error = ""
    current_stage = "preprocessamento"

    def pipeline():
        global current_stage, cancel_flag, current_error

        try:
            total = len(saved_filenames)

            for i, filename in enumerate(saved_filenames, start=1):
                if cancel_flag:
                    print("Pipeline cancelado no preprocessamento")
                    current_stage = "idle"
                    return

                current_stage = f"preprocessamento|{i}|{total}"

                preprocessing.preprocess_image(
                    input_path=str(original_dir / filename),
                    output_base_dir=str(processed_dir),
                    strategy=strategy
                )

            sfm_input_dir = processed_dir / strategy

            if cancel_flag:
                print("Pipeline cancelado antes do SfM")
                current_stage = "idle"
                return

            current_stage = "sfm_features"
            sfm.run_sfm(str(sfm_input_dir))

            if cancel_flag:
                print("Pipeline cancelado antes do MVS")
                current_stage = "idle"
                return

            current_stage = "mvs_depth"
            mvs.run_mvs(str(sfm_input_dir))

            if cancel_flag:
                print("Pipeline cancelado antes da malha")
                current_stage = "idle"
                return

            current_stage = "mesh_loading"
            meshing.generate_mesh(depth=depth, invert_normals=invert_normals)
            print(f"Depth selecionado: {depth}")

            if cancel_flag:
                print("Pipeline cancelado antes da exportação")
                current_stage = "idle"
                return

            current_stage = "exporting"
            export.export_mesh()

            current_stage = "done"
            print("Pipeline finalizado")

        except Exception as e:
            current_error = str(e)
            current_stage = "error"
            print("Erro no pipeline:", e)

    pipeline_thread = threading.Thread(target=pipeline, daemon=True)
    pipeline_thread.start()

    return jsonify({"status": "ok"})


@app.route("/status", methods=["GET"])
def status():
    global current_stage, current_error
    return jsonify({
        "stage": current_stage,
        "error": current_error
    })


@app.route("/cancel", methods=["POST"])
def cancel():
    global cancel_flag, current_stage, current_error

    cancel_flag = True
    current_stage = "idle"
    current_error = "cancelled"

    return jsonify({"status": "cancelled"})