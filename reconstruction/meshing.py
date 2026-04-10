import open3d as o3d
from pathlib import Path
import numpy as np
import time

# função principal para gerar a malha a partir da nuvem de pontos densa (chamada no arquivo com Flask)
def generate_mesh(depth=10, invert_normals=False, cancel_check=None):

    startTime = time.time()

    print("\n[Meshing]\n")

    COLMAP_PATH = Path("colmap")
    FUSED_PATH = COLMAP_PATH / "dense" / "fused.ply"
    OUTPUT_PATH = Path("static") / "models" / "mesh.ply"

    # verifica cancelamento antes de começar
    if cancel_check and cancel_check():
        raise Exception("cancelled")

    if not FUSED_PATH.exists():
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)
    pointsAmount = len(pointCloud.points)

    # verifica cancelamento após carregar nuvem
    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # calcula tamanho da cena com bounding box e diagonal
    bbox = pointCloud.get_axis_aligned_bounding_box()
    diag = np.linalg.norm(bbox.get_extent())

    maxPoints = 1005000
    downsampledPointsAmount = pointsAmount

    # downsample da nuvem se necessário
    if pointsAmount > maxPoints:
        print("\nCalculando o melhor voxel para Downsampling...\n")

        bestVoxelSize = get_best_voxel_size(pointCloud, diag, maxPoints, cancel_check)

        if cancel_check and cancel_check():
            raise Exception("cancelled")

        pointCloud = pointCloud.voxel_down_sample(bestVoxelSize)
        downsampledPointsAmount = len(pointCloud.points)

        print(f"\nVoxel size usado: {bestVoxelSize:.8f}")
        print(f"Downsample: {downsampledPointsAmount} pontos 3D\n")
    else:
        print(f"\nSem Downsample: {pointsAmount} pontos 3D\n")

    print("\nGerando a malha...\n")

    # verifica cancelamento antes de continuar
    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # recalcula tamanho da cena após downsample
    bbox = pointCloud.get_axis_aligned_bounding_box()
    diag = np.linalg.norm(bbox.get_extent())

    # raios adaptativos
    radiusNormals = diag * 0.01
    radiusOutlier = diag * 0.02

    # remove outliers estatísticos
    pointCloud, ind = pointCloud.remove_statistical_outlier(
        nb_neighbors=20,
        std_ratio=2.0
    )

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # remove outliers de raio
    pointCloud, ind = pointCloud.remove_radius_outlier(
        nb_points=16,
        radius=radiusOutlier
    )

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # estima normais
    pointCloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(
            radius=radiusNormals,
            max_nn=30
        )
    )

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    pointCloud.orient_normals_consistent_tangent_plane(100)

    # gera a malha usando Poisson Surface Reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pointCloud,
        depth=depth,
        scale=1.1,
        linear_fit=True
    )

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # organiza as densidades para remover outliers da malha
    densities = np.asarray(densities)
    threshold = np.quantile(densities, 0.10)

    vertices_to_remove = densities < threshold
    mesh.remove_vertices_by_mask(vertices_to_remove)

    # mais camada de otimização da malha
    mesh.remove_duplicated_vertices()
    mesh.remove_duplicated_triangles()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # suavização taubin
    mesh = mesh.filter_smooth_taubin(number_of_iterations=3)

    # simplifica a malha
    triangles = len(mesh.triangles)
    target = min(triangles, 400000)

    mesh = mesh.simplify_quadric_decimation(target)

    mesh.remove_unreferenced_vertices()
    mesh.compute_vertex_normals()

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    # mantém apenas o maior cluster de triângulos para garantir uma malha conectada
    triangleClusters, clusterNTriangles, clusterArea = (
        mesh.cluster_connected_triangles()
    )

    triangleClusters = np.asarray(triangleClusters)
    clusterNTriangles = np.asarray(clusterNTriangles)

    largestCluster = clusterNTriangles.argmax()
    trianglesToRemove = triangleClusters != largestCluster

    mesh.remove_triangles_by_mask(trianglesToRemove)
    mesh.remove_unreferenced_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()

    # recalcula normais após remover clusters
    mesh.compute_vertex_normals()

    # remove vértices inválidos (NaN/Inf)
    vertices = np.asarray(mesh.vertices)
    valid = np.isfinite(vertices).all(axis=1)
    mesh.remove_vertices_by_mask(~valid)

    if len(mesh.triangles) == 0:
        raise RuntimeError("Malha vazia após reconstrução.")

    if invert_normals:
        print("\nInvertendo normais da malha...\n")
        triangles = np.asarray(mesh.triangles)
        mesh.triangles = o3d.utility.Vector3iVector(triangles[:, [0, 2, 1]])
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()

    if cancel_check and cancel_check():
        raise Exception("cancelled")

    endTime = time.time()
    difTime = endTime - startTime

    # garante diretório e salva a malha
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
    print("Tempo gasto (Meshing):", f"{difTime/60:.2f}", "minutos")
    print("Mesh gerada e otimizada com sucesso!")
    print("*"*50)
    print()


# função para encontrar o melhor voxel a fim de reduzir a quantidade de pontos 3D da nuvem
def get_best_voxel_size(pointCloud, diag, maxPoints, cancel_check=None):

    initialVoxelSize = diag * 0.00005
    increaser = 1.05
    
    voxelSize = initialVoxelSize
    testPointCloud = pointCloud.voxel_down_sample(voxelSize)

    while len(testPointCloud.points) > maxPoints:

        if cancel_check and cancel_check():
            raise Exception("cancelled")

        voxelSize *= increaser
        testPointCloud = pointCloud.voxel_down_sample(voxelSize)

    return voxelSize

#generate_mesh() # teste local