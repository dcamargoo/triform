import pycolmap
import open3d as o3d
import numpy as np
from pathlib import Path


def load_sparse_as_pointcloud(sparse_path):

    if not Path(sparse_path).exists():
        raise RuntimeError(f"Pasta não encontrada: {sparse_path}")

    # carrega reconstrução (bin do COLMAP)
    reconstruction = pycolmap.Reconstruction(sparse_path)

    if len(reconstruction.points3D) == 0:
        raise RuntimeError("Nenhum ponto 3D encontrado na reconstrução")

    # extrai pontos
    xyz = np.array([p.xyz for p in reconstruction.points3D.values()])

    # extrai cores (se existirem)
    colors = np.array([p.color for p in reconstruction.points3D.values()]) / 255.0

    # cria point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)

    if len(colors) > 0:
        pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd


def visualize_sparse(pcd):
    
    print(pcd)
    print("\nPontos 3D (SfM):", len(pcd.points), "\n")

    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":

    # caminho padrão do seu projeto
    sparse_dir = Path("../colmap") / "sparse" / "0"

    print("\n[Visualização SfM - Nuvem Esparsa]\n")

    pcd = load_sparse_as_pointcloud(sparse_dir)
    visualize_sparse(pcd)