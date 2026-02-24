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

    # prepara o MVS usando a nuvem de pontos gerada pelo SfM e as imagens originais
    pycolmap.undistort_images(
        output_path=DENSE_DIR,
        image_path=IMAGE_DIR,
        input_path=SPARSE_DIR
    )

    options = pycolmap.PatchMatchOptions()
    options.max_image_size = 1600       
    options.num_iterations = 5           
    options.num_samples = 10            
    options.window_radius = 5            
    options.filter = True                
    
    # executa o PatchMatch Stereo para gerar a nuvem de pontos densa e calcular as profundidades seguindo as opções definidas
    pycolmap.patch_match_stereo(
        str(DENSE_DIR),
        options=options
    )

    fusion_options = pycolmap.StereoFusionOptions()
    fusion_options.min_num_pixels = 3
    fusion_options.max_reproj_error = 2

    # executa a remoção de outliers e a fusão para criar a nuvem de pontos final
    pycolmap.stereo_fusion(
        output_path=str(DENSE_DIR / "fused.ply"),
        workspace_path=str(DENSE_DIR),
        options=fusion_options
    )   
    
    print("MVS finalizado com sucesso!")

# run_mvs() # teste local