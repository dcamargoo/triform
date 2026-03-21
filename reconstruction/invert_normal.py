import open3d as o3d
import numpy as np
from pathlib import Path

INPUT_PATH = Path("../static/models/mesh.ply")
OUTPUT_PATH = Path("../static/models/mesh.ply")

mesh = o3d.io.read_triangle_mesh(str(INPUT_PATH))

if mesh.is_empty():
    raise RuntimeError("\nA malha está vazia ou não pôde ser carregada!\n")

# inverte a orientação dos triângulos
triangles = np.asarray(mesh.triangles)
mesh.triangles = o3d.utility.Vector3iVector(triangles[:, [0, 2, 1]])

# recalcula as normais
mesh.compute_vertex_normals()
mesh.compute_triangle_normals()

# sobrescreve a própria mesh.ply
o3d.io.write_triangle_mesh(str(OUTPUT_PATH), mesh)

print("\nMalha invertida com sucesso e sobrescrita em:", OUTPUT_PATH)
print("Vértices:", len(mesh.vertices))
print("Triângulos:", len(mesh.triangles), "\n")