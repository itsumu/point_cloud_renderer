import os
import sys
import bpy

ROOT_DIR = bpy.path.abspath('//')
IMAGES_DIR = os.path.join(ROOT_DIR, 'images')
INPUT_DIR = os.path.join(ROOT_DIR, 'inputs')
category = '03001627'
sys.path.insert(1, ROOT_DIR)
OFFSET = False

import numpy as np
from PIL import Image
import h5py
import time
import mathutils
from point_cloud_maker import PointCloudMaker

def quaternion2matrix(quaternion):
    x, y, z, w = quaternion[0], quaternion[1], quaternion[2], quaternion[3]
    xx2 = 2 * x * x
    yy2 = 2 * y * y
    zz2 = 2 * z * z
    xy2 = 2 * x * y
    wz2 = 2 * w * z
    zx2 = 2 * z * x
    wy2 = 2 * w * y
    yz2 = 2 * y * z
    wx2 = 2 * w * x
    R = np.array([[1.0 - yy2 - zz2, xy2 - wz2, zx2 + wy2, 0.0],
                  [xy2 + wz2, 1.0 - xx2 - zz2, yz2 - wx2, 0.0],
                  [zx2 - wy2, yz2 + wx2, 1.0 - xx2 - yy2, 0.0],
                  [0.0, 0.0, 0.0, 1.0]])
    return R

def translation2matrix(trans):
    T = np.eye(4, dtype=np.float32)
    T[0, 3] = trans[0]
    T[1, 3] = trans[1]
    T[2, 3] = trans[2]
    return T

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

def reset(pcm=None, clear_instancers=False, clear_database=False):
    # start_time = time.time()

    if (clear_instancers):
        # Clear materials
        for material in bpy.data.materials:
            if ('Material' in material.name) or ('material' in material.name):
                bpy.data.materials.remove(material)

    # Delete previously created instancers
    # def delete_hierarchy(obj):
    #     for child in obj.children:
    #         delete_hierarchy(child)
    #     obj.select_set(True)
    #     bpy.ops.object.delete()
    #
    # active_object = bpy.context.active_object
    # for object in bpy.context.scene.objects:
    #     if 'Plane' in object.name:
    #         active_target_name = str(active_object.name)
    #         active_object.select_set(False)
    #         delete_hierarchy(object)
    #         active_object = bpy.data.objects[active_target_name]

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

def render_one_group(object_name_list, color_list, image_path, points_list):
    print('Creating points...')
    pcm = PointCloudMaker()
    reset(clear_instancers=True)

    print('Meshing...')
    # Create spheres from point clouds
    for i, (points, object_name, color) in enumerate(
            zip(points_list, object_name_list, color_list)):
        pcm.convert_to_spheres(points, object_name, color)
        pcm.post_process()

    print('Rendering into image...')

    # start_time = time.time()

    bpy.context.scene.render.filepath = image_path
    bpy.ops.render.render(write_still=True)

    # print('render time: ', time.time() - start_time)

    reset(pcm, clear_instancers=True)  # Clear scene

# Crop rendered images & Concat them
def concat_images(output_path_list, output_path):
    # start_time = time.time()

    images = [Image.open(filename) for filename in output_path_list]

    # Crop images to resolution of crop_width * crop_width
    crop_width = 720
    # offset_left = 90  # Box frame
    # offset_right = 40  # Box frame

    offset_left = 120  # Box frame
    offset_right = 120  # Box frame

    center = (images[0].width / 2, images[1].height / 2)
    start_point = [dim - crop_width / 2 for dim in center]
    crop_area = (start_point[0] + offset_left, start_point[1],
                 start_point[0] + crop_width - offset_right, start_point[1] + crop_width)
    images = [image.crop(crop_area) for image in images]
    width = len(images) * images[0].width
    height = images[0].height

    output = Image.new('RGBA', (width, height))
    offset = 0
    for image in images:
        output.paste(image, (offset, 0))
        offset += image.width
    output.save(output_path)

# print('concat time: ', time.time() - start_time)

def start_render():
    preset_scene(category)
    reset(clear_database=True)

    gray = 'Gray'
    blue = 'Blue'
    orange = 'Orange'
    output_filename_list = ['1.png', '2.png', '3.png', '4.png',
                            '5.png', '6.png', '7.png', '8.png']
    output_path_list = [os.path.join(IMAGES_DIR, 'temp', output_filename)
                        for output_filename in output_filename_list]

    with h5py.File(os.path.join(INPUT_DIR, 'pair.h5'), 'r') as f:
        in_pts1 = np.array(f['in_pts1'])
        in_pts2 = np.array(f['in_pts2'])
        gt_pts1 = np.array(f['gt_pts1'])
        gt_pts2 = np.array(f['gt_pts2'])
        out_pts1 = np.array(f['out_pts1'])
        out_pts2 = np.array(f['out_pts2'])
        out_para21_r = np.array(f['out_para21_r'])
        out_para12_r = np.array(f['out_para12_r'])
        out_para21_t = np.array(f['out_para21_t'])
        out_para12_t = np.array(f['out_para12_t'])
        gt_matrix_1 = np.array(f['gt_matrix_1'])
        gt_matrix_2 = np.array(f['gt_matrix_2'])
        # pts_name = np.array(f['pts_name'])
        pts_name = np.array(['gallery'])

    start_iter = 0
    end_iter = len(pts_name)

    for i in range(start_iter, 1):
        start_time = time.time()

        out_R21 = quaternion2matrix(out_para21_r)
        out_R12 = quaternion2matrix(out_para12_r)
        out_T21 = translation2matrix(out_para21_t)
        out_T12 = translation2matrix(out_para12_t)
        out_M21 = np.matmul(out_T21, out_R21)
        out_M12 = np.matmul(out_T12, out_R12)
        ##################################################

        # in1
        obj_name_list = ['in_1']
        color_list = [blue]
        image_path = output_path_list[0]
        render_one_group(obj_name_list, color_list, image_path, [in_pts1])

        # in2
        obj_name_list = ['in_2']
        color_list = [orange]
        image_path = output_path_list[1]
        render_one_group(obj_name_list, color_list, image_path, [in_pts2])

        # gt1 in1 in2
        bpy.ops.import_scene.obj(
            filepath=os.path.join(INPUT_DIR, 'mesh_normalized.obj'),
            use_smooth_groups=False, use_split_objects=False,
            use_image_search=False, axis_forward='Z')

        for object in bpy.context.collection.objects:
            object.data.materials.clear()
            object.active_material = bpy.data.materials['TransparentGray']
            local_bbox_center = 0.125 * sum((mathutils.Vector(b) for b in object.bound_box), mathutils.Vector())
            global_bbox_center = object.matrix_world @ local_bbox_center
            object.select_set(True)
            bpy.ops.transform.translate(value=-global_bbox_center)
            object.select_set(False)

            original_matrix = object.matrix_world.copy()

        obj_name_list = ['in_1', 'in_2']
        color_list = [blue, orange]
        image_path = output_path_list[2]
        in_pts1_init = transform_pts(in_pts1, np.linalg.inv(gt_matrix_1))
        in_pts2_init = transform_pts(in_pts2, np.linalg.inv(gt_matrix_2))
        render_one_group(obj_name_list, color_list, image_path,
                         [in_pts1_init, in_pts2_init])
        reset(clear_database=True)

        # in2 in1 gt2
        obj_name_list = ['gt_point2', 'in_2', 'in_1']
        color_list = [gray, orange, blue]
        image_path = output_path_list[3]
        render_one_group(obj_name_list, color_list, image_path,
                         [gt_pts2, in_pts2, transform_pts(in_pts1, out_M12)])

        # out_1
        obj_name_list = ['out_point1']
        color_list = [blue]
        image_path = output_path_list[4]
        render_one_group(obj_name_list, color_list, image_path,
        				 [np.concatenate((in_pts1, out_pts1), 0)])

        # out_2
        obj_name_list = ['out_point2']
        color_list = [orange]
        image_path = output_path_list[5]
        render_one_group(obj_name_list, color_list, image_path,
        				 [np.concatenate((in_pts2, out_pts2), 0)])

        # gt_1
        obj_name_list = ['gt_point1']
        color_list = [blue]
        image_path = output_path_list[6]
        render_one_group(obj_name_list, color_list, image_path,
        				 [np.concatenate((in_pts1, gt_pts1), 0)])

        # gt_2
        obj_name_list = ['gt_point2']
        color_list = [orange]
        image_path = output_path_list[7]
        render_one_group(obj_name_list, color_list, image_path,
        				 [np.concatenate((in_pts2, gt_pts2), 0)])

        print("Concatenating images...")
        concat_images(output_path_list, os.path.join(IMAGES_DIR, str(pts_name[0]) + '.png'))
        print("Completed (%d / %d)" % (i, end_iter))
        print("Time for this image: %.2f" % (time.time() - start_time))

        reset(clear_database=True)

if __name__ == "__main__":
    start_render()
    print("Done")
