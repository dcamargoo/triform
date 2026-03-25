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
VALID_STRATEGIES = {"com_fundo", "sem_fundo"}

# rotas do Flask
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_file(Path("static/models") / filename)


@app.route("/upload", methods=["POST"])
def upload():
    # recebe as imagens e inicia pipeline de reconstrução
    global current_stage, cancel_flag, pipeline_thread

    uploaded_files = request.files.getlist("file")
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

    if processed_dir.exists():
        shutil.rmtree(processed_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    original_dir.mkdir(parents=True, exist_ok=True)

    # salva arquivos originais
    for file in uploaded_files:
        if file.filename:
            original_path = original_dir / file.filename
            file.save(original_path)

    # reseta flag de cancelamento
    cancel_flag = False
    current_stage = "preprocessamento"

    # inicia pipeline em thread
    def pipeline():
        global current_stage, cancel_flag

        # pré-processamento
        for file in uploaded_files:
            if cancel_flag:
                print("Pipeline cancelado no preprocessamento")
                current_stage = "idle"
                return

            preprocessing.preprocess_image(
                input_path=str(original_dir / file.filename),
                output_base_dir=str(processed_dir),
                strategy=strategy
            )

        sfm_input_dir = processed_dir / strategy

        # SfM
        current_stage = "sfm"
        if cancel_flag:
            print("Pipeline cancelado antes do SfM")
            current_stage = "idle"
            return
        sfm.run_sfm(str(sfm_input_dir))

        # MVS
        current_stage = "mvs"
        if cancel_flag:
            print("Pipeline cancelado antes do MVS")
            current_stage = "idle"
            return
        mvs.run_mvs(str(sfm_input_dir))

        # meshing
        current_stage = "mesh"
        if cancel_flag:
            print("Pipeline cancelado antes da malha")
            current_stage = "idle"
            return
        meshing.generate_mesh(depth=depth, invert_normals=invert_normals)
        print(f"Depth selecionado: {depth}")

        # exportar formatos
        if cancel_flag:
            print("Pipeline cancelado antes da exportação")
            current_stage = "idle"
            return
        export.export_mesh()

        current_stage = "done"
        print("Pipeline finalizado")

    pipeline_thread = threading.Thread(target=pipeline)
    pipeline_thread.start()

    return {"status": "ok"}


@app.route("/cancel", methods=["POST"])
def cancel():
    # cancelamento do pipeline
    global cancel_flag, current_stage
    cancel_flag = True
    current_stage = "idle"
    return jsonify({"status": "cancelled"})


@app.route("/status")
def status():
    # retorna a etapa atual do processamento em JSON
    global current_stage
    return jsonify({"stage": current_stage})


@app.route("/download/<format>")
def download_model(format):

    # exportação de formatos
    formats = {
        "ply": "mesh.ply",
        "obj": "mesh.obj",
        "stl": "mesh.stl",
        "glb": "mesh.glb"
    }

    if format not in formats:
        return "Formato não disponível", 404

    path = Path("static/models") / formats[format]

    if not path.exists():
        return "Arquivo ainda não gerado", 404

    return send_file(path, as_attachment=True)


def reset_pipeline():
    # função para resetar estado do pipeline (usada em testes)
    global current_stage, cancel_flag, pipeline_thread
    cancel_flag = False
    current_stage = "idle"
    pipeline_thread = None


# executa app Flask
if __name__ == "__main__":
    app.run(debug=True)