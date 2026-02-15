import open3d as o3d
from pathlib import Path
import os
import numpy as np

# gerando a malha com Poisson Surface Reconstruction, usando a nuvem de pontos densa gerada pelo MVS e otimizando a malha resultante (removendo partes ruins e suavizando)
def generate_mesh():
    DATASET_PATH = Path("colmap")
    FUSED_PATH = DATASET_PATH / "dense" / "fused.ply"
    OUTPUT_PATH = Path("static") / "models" / "mesh.ply"

    if not os.path.exists(FUSED_PATH):
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    # capturando a nuvem de pontos densa gerada pelo MVS
    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)

    # removendo ruídos da nuvem
    pointCloud, ind = pointCloud.remove_statistical_outlier(
        nb_neighbors=20,
        std_ratio=2.0
    )

    # estima normais (orientação)
    pointCloud.estimate_normals()

    # gerando a malha usando Poisson Surface Reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pointCloud,
        depth=10 # define a quantidade de polígonos na malha (resolução)
    )

    # organizando as densidades para remover partes ruins da malha
    densities = np.asarray(densities)
    threshold = np.quantile(densities, 0.10)

    vertices_to_remove = densities < threshold
    mesh.remove_vertices_by_mask(vertices_to_remove)

    mesh.remove_duplicated_vertices()
    mesh.remove_duplicated_triangles()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()

    # suavização taubin
    mesh = mesh.filter_smooth_taubin(number_of_iterations=10)
    mesh.compute_vertex_normals()

    os.makedirs("../static/models", exist_ok=True)

    # salvando a malha gerada
    o3d.io.write_triangle_mesh(OUTPUT_PATH, mesh)

    print("Mesh gerada e otimizada com sucesso!")

#generate_mesh() # teste local