# testando a visualização da nuvem de pontos densa

import open3d as o3d

pointCloud = o3d.io.read_point_cloud("../colmap/dense/fused.ply")

print(pointCloud)
print("Pontos:", len(pointCloud.points))

o3d.visualization.draw_geometries([pointCloud])