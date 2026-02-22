import pycolmap
from pathlib import Path
import shutil

# função principal para executar o SfM (chamada no arquivo com Flask)
def run_sfm(image_dir=None):
    COLMAP_PATH = Path("colmap")
    IMAGE_DIR = Path(image_dir) if image_dir else COLMAP_PATH / "images"
    SPARSE_ROOT = COLMAP_PATH / "sparse"
    SPARSE_DIR = SPARSE_ROOT / "0"

    if not IMAGE_DIR.exists():
        raise RuntimeError(f"Pasta de imagens não encontrada: {IMAGE_DIR}")

    # limpa sparse antigo
    if SPARSE_ROOT.exists():
        shutil.rmtree(SPARSE_ROOT)
    SPARSE_DIR.mkdir(parents=True)

    database = COLMAP_PATH / "database.db"
    if database.exists():
        database.unlink()

    pycolmap.extract_features(database, IMAGE_DIR)
    pycolmap.match_exhaustive(database)
    maps = pycolmap.incremental_mapping(database, IMAGE_DIR, SPARSE_DIR)

    if len(maps) == 0:
        raise RuntimeError("Nenhuma reconstrução válida foi criada!")
    else:
        print("Reconstruções válidas:", len(maps))

    maps[0].write(SPARSE_DIR)
    print("SfM finalizado com sucesso!")

# run_sfm() # teste local