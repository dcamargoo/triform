# testando a visualização da nuvem de pontos densa

import open3d as o3d

pointCloud = o3d.io.read_point_cloud("../colmap/dense/fused.ply")

print(pointCloud)
print("\nPontos 3D:", len(pointCloud.points), "\n")

o3d.visualization.draw_geometries([pointCloud])