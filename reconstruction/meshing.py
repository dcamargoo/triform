import open3d as o3d
from pathlib import Path
import numpy as np

# gerando a malha com Poisson Surface Reconstruction, usando a nuvem de pontos densa gerada pelo MVS e otimizando a malha resultante (removendo partes ruins e suavizando)
def generate_mesh():
    COLMAP_PATH = Path("colmap")
    FUSED_PATH = COLMAP_PATH / "dense" / "fused.ply"
    OUTPUT_PATH = Path("static") / "models" / "mesh.ply"

    if not FUSED_PATH.exists():
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    # capturando a nuvem de pontos densa gerada pelo MVS
    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)

    # removendo ruídos da nuvem
    pointCloud, ind = pointCloud.remove_statistical_outlier(
        nb_neighbors=20,
        std_ratio=2.0
    )

    # estima normais (orientação)
    pointCloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=0.02,
            max_nn=30
        )
    )

    # gerando a malha usando Poisson Surface Reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pointCloud,
        depth=10 # define a quantidade de polígonos na malha (resolução) por padrão deixaremos 10
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

    # remove vértices inválidos (NaN/Inf) que quebram o Three.js
    vertices = np.asarray(mesh.vertices)
    valid = np.isfinite(vertices).all(axis=1)
    mesh.remove_vertices_by_mask(~valid)

    # salvando a malha gerada (modelo 3D otimizado)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    o3d.io.write_triangle_mesh(OUTPUT_PATH, mesh)

    print("Mesh gerada e otimizada com sucesso!")

#generate_mesh() # teste local