# testando a visualização do fused.ply usando Open3D

import open3d as o3d

# caminho para o fused.ply
pcd = o3d.io.read_point_cloud("../colmap/dense/fused.ply")

print(pcd)  # sanity check
print("Pontos:", len(pcd.points))

o3d.visualization.draw_geometries([pcd])