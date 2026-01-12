# importando o pycolmap e outras bibliotecas necessárias
import pycolmap
from pathlib import Path

# função principal para executar o SfM (chamada no arquivo Flask)
def run_sfm():

    image_dir = Path("colmap/images")
    sparse_dir = Path("colmap/sparse")

    if not image_dir.exists():
        raise RuntimeError("Pasta 'images' não encontrada")

    database = sparse_dir / "database.db"

    # detecção e descrição de features com SIFT
    pycolmap.extract_features(database, image_dir)

    # correspondência (Matching) exaustiva/não sequencial de features 
    pycolmap.match_exhaustive(database)

    # SfM incremental (poses + triangulação + refinamentos + BA internos)
    maps = pycolmap.incremental_mapping(database, image_dir, sparse_dir)

    if len(maps) == 0:
        raise RuntimeError("Nenhuma reconstrução válida foi criada!")
    else:   
        print("Reconstruções válidas:", len(maps))

    maps[0].write(sparse_dir)

run_sfm()