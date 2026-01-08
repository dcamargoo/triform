import pycolmap

# função que executa o Structure from Motion (SfM)
def run_sfm(arg_image_dir, arg_output_dir, arg_database_path):
    
    # detecção e descrição de features com SIFT
    pycolmap.extract_features(
        database_path=arg_database_path,
        image_path=arg_image_dir
    )

    # correspondência (Matching) exaustiva de features
    pycolmap.match_exhaustive(database_path=arg_database_path)

    # RANSAC para verificar os matches encontrados
    pycolmap.verify_matches(database_path=arg_database_path)

    # SfM incremental (poses + triangulação + refinamentos + BA internos)
    reconstruction = pycolmap.incremental_mapping(
        database_path=arg_database_path,
        image_path=arg_image_dir,
        output_path=arg_output_dir,
    )

    # pegando a maior reconstrução
    bestReconstruction = max(reconstruction, key=lambda r: len(r.images))
    
    return bestReconstruction

    # testando o resultado da função
    print("Quantidade de imagens registradas:", len(bestReconstruction.images))
    print("Pontos 3D:", len(bestReconstruction.points3D))