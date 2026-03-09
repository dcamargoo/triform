import open3d as o3d
from pathlib import Path
import numpy as np
import trimesh

# gerando a malha com Poisson Surface Reconstruction, usando a nuvem de pontos densa gerada pelo MVS e otimizando a malha resultante (removendo partes ruins e suavizando)
def generate_mesh():
    COLMAP_PATH = Path("colmap")
    FUSED_PATH = COLMAP_PATH / "dense" / "fused.ply"
    
    MODEL_PATH = Path("static") / "models"

    PLY_PATH = MODEL_PATH / "mesh.ply"
    OBJ_PATH = MODEL_PATH / "mesh.obj"
    STL_PATH = MODEL_PATH / "mesh.stl"
    GLB_PATH = MODEL_PATH / "mesh.glb"

    if not FUSED_PATH.exists():
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    # capturando a nuvem de pontos densa gerada pelo MVS
    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)

    # removendo ruídos da nuvem
    pointCloud, ind = pointCloud.remove_statistical_outlier(
        nb_neighbors=20,
        std_ratio=2.0
    )

    # estima normais (orientação) de acordo com o tamanho da cena
    bbox = pointCloud.get_axis_aligned_bounding_box()
    diag = np.linalg.norm(bbox.get_extent())
    radius = diag * 0.01
    pointCloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=radius,
            max_nn=30
        )
    )

    # orientando as normais de forma consistente para evitar problemas na geração da malha
    pointCloud.orient_normals_consistent_tangent_plane(100)

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
    mesh = mesh.filter_smooth_taubin(number_of_iterations=5)
    mesh.compute_vertex_normals()

    # remove vértices inválidos (NaN/Inf)
    vertices = np.asarray(mesh.vertices)
    valid = np.isfinite(vertices).all(axis=1)
    mesh.remove_vertices_by_mask(~valid)

    # criar pasta models
    MODEL_PATH.mkdir(parents=True, exist_ok=True)

    # salvar PLY
    o3d.io.write_triangle_mesh(PLY_PATH, mesh)

    # salvar OBJ e STL
    o3d.io.write_triangle_mesh(OBJ_PATH, mesh)
    o3d.io.write_triangle_mesh(STL_PATH, mesh)

    # converter para GLB usando trimesh
    tri_mesh = trimesh.load(PLY_PATH)
    tri_mesh.export(GLB_PATH)

    print("Mesh gerada com sucesso!")
    print("Formatos disponíveis:")
    print("PLY, OBJ, STL, GLB")

# generate_mesh() # teste local