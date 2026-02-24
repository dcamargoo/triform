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
    
    # executa o SIFT (detector e descritor)
    pycolmap.extract_features(database, IMAGE_DIR)
    
    # executa o matching (encontra correspondências entre as imagens) e executa o RANSAC para filtrar correspondências erradas
    pycolmap.match_exhaustive(database)
    
    # executa a triangulação incremental e o bundle adjustment para criar a reconstrução 3D
    maps = pycolmap.incremental_mapping(database, IMAGE_DIR, SPARSE_DIR)

    if len(maps) == 0:
        raise RuntimeError("Nenhuma reconstrução válida foi criada!")
    else:
        print("Reconstruções válidas:", len(maps))

    largest_map = max(maps.values(), key=lambda m: m.num_images())
    largest_map.write(SPARSE_DIR)

    print("Imagens reconstruídas:", largest_map.num_images())
    print("Pontos 3D:", largest_map.num_points3D())
    print("SfM finalizado com sucesso!")

# run_sfm() # teste local