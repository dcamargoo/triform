import pycolmap
from pathlib import Path
import shutil

# função principal para executar o MVS (chamada no arquivo com Flask)
def run_mvs(image_dir=None):
    COLMAP_PATH = Path("colmap")
    IMAGE_DIR = Path(image_dir) if image_dir else COLMAP_PATH / "images"
    SPARSE_DIR = COLMAP_PATH / "sparse/0"
    DENSE_DIR = COLMAP_PATH / "dense"

    if not SPARSE_DIR.exists():
        raise RuntimeError("Modelo SfM não encontrado em 'colmap/sparse/0'")

    if DENSE_DIR.exists():
        shutil.rmtree(DENSE_DIR)
    DENSE_DIR.mkdir(parents=True)

    pycolmap.undistort_images(
        output_path=DENSE_DIR,
        image_path=IMAGE_DIR,
        input_path=SPARSE_DIR
    )

    pycolmap.patch_match_stereo(DENSE_DIR)
    pycolmap.stereo_fusion(
        output_path=DENSE_DIR / "fused.ply",
        workspace_path=DENSE_DIR
    )
    print("MVS finalizado com sucesso!")

# run_mvs() # teste local