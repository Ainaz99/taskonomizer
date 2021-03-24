"""
  Name: create_ply_from_obj.py
  Desc: Saves obj mesh as ply mesh.
  
"""

import os
import sys
import bpy
import numpy as np
import pickle
from collections import defaultdict
from mathutils import Vector, Euler, Matrix
# from pytransform3d.rotations import *

# Import remaining packages
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from load_settings import settings
import create_images_utils
import utils
import io_utils

basepath = settings.MODEL_PATH

def import_src_obj(obj_name, is_google_obj=True):
    path = '/scratch-data/ainaz/habitat-sim/data/objects'
    if is_google_obj:
        obj_path = os.path.join(path, 'google_objects', obj_name, '{}.obj'.format(obj_name))
    else:
        obj_path = os.path.join(path, '{}.obj'.format(obj_name))

    bpy.ops.import_scene.obj(
        filepath=obj_path,
        axis_forward=settings.OBJ_AXIS_FORWARD,
        axis_up=settings.OBJ_AXIS_UP)
    obj = bpy.context.scene.objects[0]
    bpy.context.scene.objects.active = obj
    obj.select = True
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    return obj


def main():
    utils.delete_all_objects_in_context()

    model = io_utils.import_mesh(basepath)

    bbox_corners = [model.matrix_world * Vector(corner) for corner in model.bound_box]
    x_range, y_range, z_range = set(), set(), set()
    for corner in bbox_corners:
        x_range.add(corner[0])
        y_range.add(corner[1])
        z_range.add(corner[2])
    x_range = sorted(list(x_range))
    y_range = sorted(list(y_range))
    z_range = sorted(list(z_range))


    with open(os.path.join(basepath, 'objs_blender.pkl'), 'rb') as f:
        blender_objs = pickle.load(f)
    with open(os.path.join(basepath, 'objs_habitat.pkl'), 'rb') as f:
        habitat_objs = pickle.load(f)
    objs = blender_objs.copy()

    obj_counts = {}
    obj_counts = defaultdict(lambda: 0, obj_counts)
    obj_sources = {}
    invalid_objs = []
    for i, obj_info in enumerate(objs):
        pos, rot, rot_q, obj_name = obj_info[0], obj_info[1], obj_info[2], obj_info[3]
        # p, v, s, obj_name = obj_info[0], obj_info[1], obj_info[2], obj_info[3]

        # pos = np.array([p[0], -p[2], p[1]])
        # R1 = matrix_from_quaternion(
        #     [s, v[0], v[1], v[2]])
        # R_trans = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        # R2 = R_trans.dot(R1)
        # rot_q = quaternion_from_matrix(R2)
        # rot = euler_xyz_from_matrix(R2)

        out_of_bounds = False
        if pos[0] > x_range[-1] - 0.2 or pos[0] < x_range[0] + 0.2: out_of_bounds = True
        if pos[1] > y_range[-1] - 0.2 or pos[1] < y_range[0] + 0.2: out_of_bounds = True
        if pos[2] > z_range[-1] - 0.2 or pos[2] < z_range[0]: out_of_bounds = True

        if out_of_bounds:
            print("Out of bounds!")
            invalid_objs.append(i)
            continue


        obj_counts[obj_name] += 1
        if obj_counts[obj_name] == 1:
            is_google_obj = False if obj_name in ['banana', 'cheezit', 'chefcan'] else True
            obj = import_src_obj(obj_name, is_google_obj=is_google_obj)
            obj_sources[obj_name] = obj

        else:
            src = obj_sources[obj_name]
            bpy.context.scene.objects.active = src
            src.select = True

            obj = src.copy()
            obj.data = src.data.copy()
            obj.animation_data_clear()
            bpy.context.scene.objects.link(obj)
    
  
        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_q

        obj.location.x = pos[0]
        obj.location.y = pos[1]
        obj.location.z = pos[2]


    final_model = io_utils.join_meshes()  # OBJs often come in many many pieces

    save_path = os.path.join(basepath, 'mesh_with_objs.ply')

    bpy.ops.export_mesh.ply(filepath=save_path,
        axis_forward='Y',
        axis_up='Z',
        use_normals=False,
        use_uv_coords=False,
        use_colors=False)

    valid_blender_objs = [blender_objs[i] for i in range(len(blender_objs)) if i not in invalid_objs]
    valid_habitat_objs = [habitat_objs[i] for i in range(len(habitat_objs)) if i not in invalid_objs]
    with open(os.path.join(settings.MODEL_PATH, 'objs_habitat.pkl'), 'wb') as f:
        pickle.dump(valid_habitat_objs, f)
    with open(os.path.join(settings.MODEL_PATH, 'objs_blender.pkl'), 'wb') as f:
        pickle.dump(valid_blender_objs, f)

    print("Number of valid objects : ", len(valid_blender_objs), len(valid_habitat_objs))

if __name__ == "__main__":
    with utils.Profiler("simulate_drop.py"):
        main()
