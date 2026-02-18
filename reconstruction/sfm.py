import pycolmap
from pathlib import Path
import shutil

# função principal para executar o SfM (chamada no arquivo com Flask)
def run_sfm():
    COLMAP_PATH = Path("colmap")
    IMAGE_DIR = COLMAP_PATH / "images"
    SPARSE_ROOT = COLMAP_PATH / "sparse"
    SPARSE_DIR = COLMAP_PATH / "sparse" / "0"

    if not IMAGE_DIR.exists():
        raise RuntimeError("Pasta 'images' não encontrada")

    # limpa sparse antigo
    if SPARSE_ROOT.exists():
        shutil.rmtree(SPARSE_ROOT)

    SPARSE_DIR.mkdir(parents=True)

    database = COLMAP_PATH / "database.db"

    # remove o banco de dados existente para evitar conflitos
    if database.exists():
        database.unlink()

    # detecção e descrição de features com SIFT
    pycolmap.extract_features(database, IMAGE_DIR)

    # correspondência (Matching) exaustiva/não sequencial de features 
    pycolmap.match_exhaustive(database)

    # SfM incremental (poses + triangulação + refinamentos + BA internos)
    maps = pycolmap.incremental_mapping(database, IMAGE_DIR, SPARSE_DIR)

    if len(maps) == 0:
        raise RuntimeError("Nenhuma reconstrução válida foi criada!")
    else:   
        print("Reconstruções válidas:", len(maps))

    maps[0].write(SPARSE_DIR)

    print("SfM finalizado com sucesso!")

#run_sfm() # teste local