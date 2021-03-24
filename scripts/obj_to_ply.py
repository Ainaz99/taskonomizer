"""
  Name: create_ply_from_obj.py
  Desc: Saves obj mesh as ply mesh.
  
"""

import os
import sys
import bpy

# Import remaining packages
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from load_settings import settings
import create_images_utils
import utils
import io_utils

basepath = settings.MODEL_PATH

def main():
    if settings.CLEVR:
        settings.MODEL_FILE = 'point_{}_view_{}_domain_obj.obj'.format(settings.POINT, 0)
        model_fpath = os.path.join(basepath, 'obj', settings.MODEL_FILE)
        
    else:
        model_fpath = os.path.join(basepath, settings.MODEL_FILE)



    utils.delete_all_objects_in_context()

    imported_obj = bpy.ops.import_scene.obj(
            filepath=model_fpath,
            axis_forward=settings.OBJ_AXIS_FORWARD,
            axis_up=settings.OBJ_AXIS_UP) 
    model = io_utils.join_meshes()
    bpy.context.scene.objects.active = model

    model_fpath = model_fpath.replace('/obj/', '/ply/').replace('.obj', '.ply')

    bpy.ops.export_mesh.ply(filepath=model_fpath,
        axis_forward=settings.OBJ_AXIS_FORWARD,
        axis_up=settings.OBJ_AXIS_UP,
        global_scale=0.01,
        use_normals=False,
        use_uv_coords=False,
        use_colors=False)




if __name__ == "__main__":
    with utils.Profiler("obj_to_ply.py"):
        main()
