import pycolmap
from pathlib import Path
import shutil
import time

# função principal para executar o SfM (chamada no arquivo com Flask)
def run_sfm(image_dir=None):

    startTime = time.time()

    print("\n[SfM]\n")

    COLMAP_ROOT = Path("colmap")
    IMAGE_DIR = Path(image_dir) if image_dir else COLMAP_ROOT / "images"
    SPARSE_ROOT = COLMAP_ROOT / "sparse"
    SPARSE_DIR = SPARSE_ROOT / "0"

    if not IMAGE_DIR.exists():
        raise RuntimeError(f"Pasta de imagens não encontrada: {IMAGE_DIR}")

    if SPARSE_ROOT.exists():
        shutil.rmtree(SPARSE_ROOT)
    SPARSE_DIR.mkdir(parents=True)

    database = COLMAP_ROOT / "database.db"
    if database.exists():
        database.unlink()
    
    # executa o SIFT (detector e descritor de features)
    pycolmap.extract_features(database, IMAGE_DIR)
    
    # executa o matching (encontra correspondências entre as imagens) e executa o RANSAC para filtrar outliers
    pycolmap.match_exhaustive(database)

    # executa a triangulação incremental e o bundle adjustment para criar a reconstrução 3D
    recs = pycolmap.incremental_mapping(database, IMAGE_DIR, SPARSE_DIR)
    recsAmount = len(recs)

    endTime = time.time()
    difTime = endTime - startTime

    if recsAmount == 0:
        raise RuntimeError("Nenhuma reconstrução válida foi criada!")
    else:
        print()
        print("*"*50)
        print("Reconstruções válidas:", recsAmount)

    largest_rec = max(recs.values(), key=lambda m: m.num_images())
    largest_rec.write(SPARSE_DIR)

    print("Imagens reconstruídas:", largest_rec.num_images())
    print("Pontos 3D (SfM):", largest_rec.num_points3D())
    print("Tempo gasto (SfM):", f"{difTime:.2f}", "segundos")
    print("SfM finalizado com sucesso!")
    print("*"*50)
    print()

#run_sfm() # teste local