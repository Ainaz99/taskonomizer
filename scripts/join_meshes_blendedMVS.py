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

folder = basepath.split('/')[-1]
textured_mesh_path = '/scratch/ainaz/BlendedMVS/dataset_textured_meshes/'+folder+'/textured_mesh'
objs = [file for file in os.listdir(textured_mesh_path) if file.endswith('.obj')]

def import_obj(obj_name):
    obj_path = os.path.join(textured_mesh_path, obj_name)

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
    print("!!!!!!! ", len(objs))
    print(os.path.join(basepath, 'mesh.ply'))


    for i, obj_name in enumerate(objs):
        print(obj_name)

        obj = import_obj(obj_name)  
        obj.select = True
        bpy.context.scene.objects.active = obj



    final_model = io_utils.join_meshes()  # OBJs often come in many many pieces

    save_path = os.path.join(basepath, 'mesh.ply')


    bpy.ops.export_mesh.ply(filepath=save_path,
        axis_forward='Y',
        axis_up='Z',
        use_normals=False,
        use_uv_coords=False,
        use_colors=False)



    print("Number of objects : ", len(objs))

if __name__ == "__main__":
    with utils.Profiler("join_meshes_blendedMVS.py"):
        main()
