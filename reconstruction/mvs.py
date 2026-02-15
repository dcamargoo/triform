import pycolmap
from pathlib import Path
import shutil

# função principal para executar o MVS (chamada no arquivo com Flask)
def run_mvs():
    DATASET_PATH = Path("colmap")
    IMAGE_DIR = DATASET_PATH / "images"
    SPARSE_DIR = DATASET_PATH / "sparse" / "0"
    DENSE_DIR = DATASET_PATH / "dense"

    if not SPARSE_DIR.exists():
        raise RuntimeError("Modelo SfM não encontrado em 'colmap/sparse/0'")

    # limpa dense antigo
    if DENSE_DIR.exists():
        shutil.rmtree(DENSE_DIR)

    # cria pasta nova
    DENSE_DIR.mkdir(parents=True)

    # correção de distorção das imagens usando o modelo SfM
    pycolmap.undistort_images(
        output_path=DENSE_DIR,
        image_path=IMAGE_DIR,
        input_path=SPARSE_DIR
    )

    # estimativa de mapas de profundidade (PatchMatch Stereo)
    pycolmap.patch_match_stereo(DENSE_DIR)

    # fusão dos mapas de profundidade em uma nuvem de pontos densa
    pycolmap.stereo_fusion(
        output_path=DENSE_DIR / "fused.ply",
        workspace_path=DENSE_DIR
    )

    print("MVS finalizado com sucesso!")

#run_mvs() # teste local