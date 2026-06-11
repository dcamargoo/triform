import open3d as o3d
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
#arquivo = BASE_DIR / "static" / "models" / "mesh.ply"
arquivo = BASE_DIR / "static" / "models" / "mesh_escalado.ply"

mesh = o3d.io.read_triangle_mesh(str(arquivo))
mesh.compute_vertex_normals()

print(mesh)

if len(mesh.triangles) == 0:
    print("Erro: malha sem triângulos!")
    exit()

# converter para pontos
pcd = mesh.sample_points_uniformly(number_of_points=200000)

print("SHIFT + clique para selecionar 2 pontos")
print("Pressione Q para fechar")

vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.add_geometry(pcd)
vis.run()
vis.destroy_window()

idx = vis.get_picked_points()

if len(idx) != 2:
    print("Selecione exatamente 2 pontos!")
    exit()

p1 = np.asarray(pcd.points)[idx[0]]
p2 = np.asarray(pcd.points)[idx[1]]

dist_modelo = np.linalg.norm(p1 - p2)

print(f"Distância medida (modelo): {dist_modelo}")

# escolha da escala
real = float(input("Digite a medida real em cm: "))

escala = real / dist_modelo

mesh.scale(escala, center=(0, 0, 0))

print(f"Escala aplicada: {escala}")

# salvar a malha já escalada de acordo com uma medida
output = BASE_DIR / "static" / "models" / "mesh_escalado.ply"
o3d.io.write_triangle_mesh(str(output), mesh)

print(f"Malha escalada salva em: {output}")