import open3d as o3d
from pathlib import Path
import numpy as np
import time

# função principal para gerar a malha a partir da nuvem de pontos densa (chamada no arquivo com Flask)
def generate_mesh():

    startTime = time.time()

    print("\n[Meshing]\n")

    COLMAP_PATH = Path("colmap")
    FUSED_PATH = COLMAP_PATH / "dense" / "fused.ply"
    OUTPUT_PATH = Path("static") / "models" / "mesh.ply"

    if not FUSED_PATH.exists():
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)
    pointsAmount = len(pointCloud.points)

    # calcula tamanho da cena com bounding box e diagonal
    bbox = pointCloud.get_axis_aligned_bounding_box()
    diag = np.linalg.norm(bbox.get_extent())

    # downsample da nuvem
    if pointsAmount > 1200000:
        voxel_size = diag * 0.00015
        pointCloud = pointCloud.voxel_down_sample(voxel_size)

    downsampledPointsAmount = len(pointCloud.points)

    # recalcula tamanho da cena após downsample
    bbox = pointCloud.get_axis_aligned_bounding_box()
    diag = np.linalg.norm(bbox.get_extent())

    # raios adaptativos
    radius_normals = diag * 0.01
    radius_outlier = diag * 0.02

    # remove outliers estatísticos e de raio
    pointCloud, ind = pointCloud.remove_statistical_outlier(
        nb_neighbors=20,
        std_ratio=2.0
    )

    # remove outliers de raio
    pointCloud, ind = pointCloud.remove_radius_outlier(
        nb_points=16,
        radius=radius_outlier
    )

    # estima normais
    pointCloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=radius_normals,
            max_nn=30
        )
    )

    pointCloud.orient_normals_consistent_tangent_plane(100)

    # gerando a malha usando Poisson Surface Reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pointCloud,
        depth=10,
        scale=1.1,
        linear_fit=True
    )

    # organizando as densidades para remover outliers da malha
    densities = np.asarray(densities)
    threshold = np.quantile(densities, 0.10)

    vertices_to_remove = densities < threshold
    mesh.remove_vertices_by_mask(vertices_to_remove)

    # mais camada de otimização da malha
    mesh.remove_duplicated_vertices()
    mesh.remove_duplicated_triangles()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()

    # suavização taubin
    mesh = mesh.filter_smooth_taubin(number_of_iterations=3)

    # simplificação da malha
    triangles = len(mesh.triangles)
    target = min(triangles, 400000)

    mesh = mesh.simplify_quadric_decimation(target)

    mesh.remove_unreferenced_vertices()
    mesh.compute_vertex_normals()

    # remove vértices inválidos (NaN/Inf)
    vertices = np.asarray(mesh.vertices)
    valid = np.isfinite(vertices).all(axis=1)
    mesh.remove_vertices_by_mask(~valid)

    endTime = time.time()
    difTime = endTime - startTime

    # salvando a malha gerada
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    o3d.io.write_triangle_mesh(OUTPUT_PATH, mesh)

    verticesAmount = len(mesh.vertices)
    trianglesAmount = len(mesh.triangles)

    print()
    print("*"*50)
    print("Vertices:", verticesAmount)
    print("Triângulos:", trianglesAmount)
    print("Pontos 3D (MVS):", pointsAmount)
    print("Pontos 3D (Downsample):", downsampledPointsAmount)
    print("Tempo gasto (Meshing):", f"{difTime:.2f}", "segundos")
    print("Mesh gerada e otimizada com sucesso!")
    print("*"*50)
    print()

#generate_mesh() # teste local