import os
import sys
import time
import bpy

ROOT_DIR = bpy.path.abspath('//')
IMAGES_DIR = os.path.join(ROOT_DIR, 'images')
INPUT_DIR = os.path.join(ROOT_DIR, 'inputs')
category = '03001627'
sys.path.insert(1, ROOT_DIR)

import numpy as np
from point_cloud_maker import PointCloudMaker

# Apply transformation to points
def transform_pts(points, transform):
	# batch transform
	if len(transform.shape) == 3:
		rot = transform[:, :3, :3]
		trans = transform[:, :3, 3]
	# single transform
	else:
		rot = transform[:3, :3]
		trans = transform[:3, 3]
	point = np.matmul(points, np.transpose(rot)) + np.expand_dims(trans, axis=-2)
	return point

# Setup blender scene
def preset_scene(category):
	# 3D cursor settings
	bpy.context.scene.cursor.location = (0, 0, 0)
	bpy.context.scene.cursor.rotation_euler = (0, 0, 0)
	bpy.ops.object.select_all(action='DESELECT')
	bpy.data.objects['Origin'].select_set(True)
	bpy.context.view_layer.objects.active = bpy.data.objects['Origin']

	# Set up z axis length
	z_axis_length_table = {
		'02691156': 0.6,
		'02933112': 0.9,
		'02958343': 0.6,
		'03636649': 0.9,
		'03001627': 0.9,
		'04256520': 0.6,
		'04379243': 0.6,
		'04530566': 0.6
	}
	bpy.context.scene.objects['Z-Axis'].scale.z = z_axis_length_table[category]
	bpy.context.scene.objects['Arrow'].location.z = z_axis_length_table[category]

# Clear intermediate stuff
def reset(pcm=None, clear_instancers=False, clear_database=False):
	# start_time = time.time()

	if (clear_instancers):
		# Clear materials
		for material in bpy.data.materials:
			if ('Material' in material.name) or ('material' in material.name):
				bpy.data.materials.remove(material)

	if pcm != None:
		pcm.clear_instancers()
	if clear_database:
		# Clear meshes
		for mesh in bpy.data.meshes:
			if (not 'Cube' in mesh.name) and (not 'Cone' in mesh.name) \
					and (not 'Cylinder' in mesh.name):
				bpy.data.meshes.remove(mesh)

		# Clear images
		for image in bpy.data.images:
			bpy.data.images.remove(image)
	# print('reset time: ', time.time() - start_time)

if __name__ == "__main__":
	image_path = os.path.join(IMAGES_DIR, 'chair.png')
	sphere_color = 'Blue'
	sphere_radius = 0.02

	# Generate point cloud from file
	print('Generating point cloud...')
	pcm = PointCloudMaker()
	pcd = pcm.generate_points_from_pts(os.path.join(INPUT_DIR, 'chair.pts'))
	reset(clear_instancers=True)

	# Create spheres from point clouds
	print('Meshing...')
	pcm.convert_to_spheres(points=pcd, object_name='chair', color=sphere_color, sphere_radius=sphere_radius)
	pcm.post_process()

	print('Rendering into image...')

	# start_time = time.time()

	bpy.context.scene.render.filepath = image_path
	bpy.ops.render.render(write_still=True)

	# print('render time: ', time.time() - start_time)

	reset(pcm, clear_instancers=True)  # Clear scene
	print("Done")

