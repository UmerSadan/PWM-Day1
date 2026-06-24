import numpy as np
import open3d as o3d

print("--- Step 1: Generating Synthetic 3D Spatial Data ---")
# Create a mathematical 3D Mobius strip point cloud to simulate an artifact scan
n_u = 200   # resolution along the strip's length
n_v = 25    # resolution across the strip's width
u = np.linspace(0, 2 * np.pi, n_u)
v = np.linspace(-1, 1, n_v)
u, v = np.meshgrid(u, v)
u = u.flatten()
v = v.flatten()

# Parametric equations mapping 2D parameters to 3D Spatial coordinates (X, Y, Z)
x = (1 + 0.5 * v * np.cos(u / 2)) * np.cos(u)
y = (1 + 0.5 * v * np.cos(u / 2)) * np.sin(u)
z = 0.5 * v * np.sin(u / 2)
xyz = np.vstack((x, y, z)).T

# Instantiate into an Open3D Spatial Point Cloud object
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(xyz)
print(f"Successfully generated point cloud with {len(pcd.points)} spatial vectors.")

print("\n--- Step 2: Estimating Vertex Surface Normals ---")
# 3D algorithms need to know which direction a surface faces to calculate light reflection
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
# Ball Pivoting is very sensitive to normal *direction* (not just presence) —
# this makes neighboring normals point consistently the same way.
pcd.orient_normals_consistent_tangent_plane(30)
print("Surface normals calculated and oriented successfully.")

print("\n--- Step 3: Executing 3D Mesh Surface Reconstruction ---")
# Using the Ball Pivoting Algorithm (BPA) to roll virtual spheres across the point cloud
# to connect the spatial coordinates into a solid 3D surface mesh topology
distances = pcd.compute_nearest_neighbor_distance()
avg_dist = np.mean(distances)
radii = [avg_dist, 2 * avg_dist]

mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
    pcd, o3d.utility.DoubleVector(radii)
)
mesh.compute_vertex_normals()
print(f"Reconstruction Complete! Generated a 3D Mesh with {len(mesh.triangles)} surface triangles.")

print("\n--- Step 4: Exporting 3D Pipeline Asset Outputs ---")
# Save the generated 3D model asset format
output_filename = "pmw_day1_reconstruction.obj"
o3d.io.write_triangle_mesh(output_filename, mesh)
print(f"Successfully saved 3D asset model file as: {output_filename}")
print("Check your left-hand sidebar folder in Google Colab to download your file!")