# importando o pycolmap e outras bibliotecas necessárias
import pycolmap
from pathlib import Path

# função principal para executar o SfM (chamada no arquivo Flask)
def run_sfm():
    IMAGE_DIR = Path("colmap/images")
    SPARSE_DIR = Path("colmap/sparse")
    DATASET_PATH = Path("colmap")

    if not IMAGE_DIR.exists():
        raise RuntimeError("Pasta 'images' não encontrada")

    database = DATASET_PATH / "database.db"

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