import open3d as o3d
import os

# gerando a malha com Poisson Surface Reconstruction, usando a nuvem de pontos densa gerada pelo MVS
def generate_mesh():

    FUSED_PATH = "../colmap/dense/fused.ply"
    OUTPUT_PATH = "../static/models/mesh.ply"

    if not os.path.exists(FUSED_PATH):
        raise RuntimeError("fused.ply não encontrado! Rode o MVS primeiro.")

    # capturando a nuvem de pontos densa gerada pelo MVS
    pointCloud = o3d.io.read_point_cloud(FUSED_PATH)

    # estima normais (orientação)
    pointCloud.estimate_normals()

    # gerando a malha usando Poisson Surface Reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pointCloud,
        depth=9
    )

    os.makedirs("../static/models", exist_ok=True)

    # salvando a malha gerada
    o3d.io.write_triangle_mesh(OUTPUT_PATH, mesh)

    print("Mesh gerada com sucesso!")

#generate_mesh() # teste local