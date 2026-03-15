import pycolmap
import open3d as o3d
from pathlib import Path
import shutil
import time

# função principal para executar o MVS (chamada no arquivo com Flask)
def run_mvs(image_dir=None):

    startTime = time.time()

    print("\n[MVS]\n")

    COLMAP_PATH = Path("colmap")
    IMAGE_DIR = Path(image_dir) if image_dir else COLMAP_PATH / "images"
    SPARSE_DIR = COLMAP_PATH / "sparse/0"
    DENSE_DIR = COLMAP_PATH / "dense"

    if not SPARSE_DIR.exists():
        raise RuntimeError("Modelo SfM não encontrado em 'colmap/sparse/0'")

    if DENSE_DIR.exists():
        shutil.rmtree(DENSE_DIR)
    DENSE_DIR.mkdir(parents=True)

    # ajuste das imagens (lente)
    pycolmap.undistort_images(
        output_path=DENSE_DIR,
        image_path=IMAGE_DIR,
        input_path=SPARSE_DIR
    )

    # configurações do PatchMatch Stereo
    options = pycolmap.PatchMatchOptions()
    options.max_image_size = 1600       
    options.num_iterations = 5        
    options.num_samples = 10          
    options.window_radius = 5            
    options.filter = True                
    
    # execução do PatchMatch Stereo para gerar a nuvem de pontos densa
    pycolmap.patch_match_stereo(
        str(DENSE_DIR),
        options=options
    )

    # configurações da Stereo Fusion
    fusion_options = pycolmap.StereoFusionOptions()
    fusion_options.min_num_pixels = 4
    fusion_options.max_reproj_error = 1
    fusion_options.max_depth_error = 0.01

    FUSED_PATH = DENSE_DIR / "fused.ply"

    # execução da Stereo Fusion para gerar a nuvem de pontos densa final (fused.ply)
    pycolmap.stereo_fusion(
        output_path=str(FUSED_PATH),
        workspace_path=str(DENSE_DIR),
        options=fusion_options
    )

    endTime = time.time()
    difTime = endTime - startTime

    # análise da nuvem de pontos densa gerada
    densePointCloud = o3d.io.read_point_cloud(str(FUSED_PATH))
    densePointsAmount = len(densePointCloud.points)

    print()
    print("*"*50)
    print(f"Pontos 3D (MVS): {densePointsAmount}")
    print(f"Tempo gasto (MVS): {difTime:.2f} segundos")
    print("MVS finalizado com sucesso!")
    print("*"*50)
    print()

#run_mvs() # teste local