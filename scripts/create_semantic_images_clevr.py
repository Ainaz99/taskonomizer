"""
  Name: create_semantic_images.py
  Author: Sasha Sax, CVGL
  Desc: Creates semantically tagged versions standard RGB images by using the matterport models and 
    semantic labels.
    This reads in all the point#.json files and rendering the corresponding images with semantic labels. 

  Usage:
    blender -b -noaudio -enable-autoexec --python create_semantic_images.py --
"""
from __future__ import division

import os
import sys
import bpy
import bpy_extras.mesh_utils
import bmesh
from collections import defaultdict, Counter
import glob
import json
import math
from mathutils import Vector, Euler, Color
import numpy as np
import random
import shutil  # Temporary dir
import time
import tempfile  # Temporary dir
import uuid as uu
from plyfile import *
import numpy as np
from scipy.signal import find_peaks

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from load_settings import settings
import io_utils
import utils
from utils import Profiler
from create_images_utils import *

TASK_NAME = 'semantic'

utils.set_random_seed()
basepath = settings.MODEL_PATH

shapes = ['cube', 'sphere', 'cylinder']
sizes = ['small', 'medium', 'large']
colors = ['red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'brown', 'gray']
materials = ['rubber', 'metal']

# R = shape + 10 * size = size,shape
# G = color + 10 * material = material,color
# B = instance

def get_face_semantics(point_info):
    """
      Find mesh faces for each object.

      Returns:
        objects: A Dict of object id to faces.
    """

    path_in = os.path.join(basepath, 'obj', settings.MODEL_FILE)

    objects = list(point_info['objects'].keys())
    objects.append('Ground_Mesh')
    print(objects)
    face_to_object = {}
    
    current_obj = ''
 
    with open(path_in, "r") as file:
        for line in file:
            
            if line.startswith('o '):
                for obj in objects:
                    if line.__contains__(obj):
                        current_obj = obj
            if line.startswith('f '):
                vertices = [int(v.split('//')[0]) - 1 for v in line.split()[1:]]   
                face_to_object[tuple(sorted(vertices))] = current_obj

    return face_to_object, objects



def main():
    global basepath
    global TASK_NAME

    point_infos = io_utils.load_saved_points_of_interest(basepath)

    for point_idx, point_info in enumerate(point_infos):
        for view_number, view_dict in enumerate(point_info):
            point_number = settings.POINT
            settings.MODEL_FILE = 'point_{}_view_{}_domain_obj.obj'.format(point_number, view_number)

            utils.delete_all_objects_in_context()

            bpy.ops.import_scene.obj(
                filepath=os.path.join(basepath, 'obj', settings.MODEL_FILE),
                axis_forward=settings.OBJ_AXIS_FORWARD,
                axis_up=settings.OBJ_AXIS_UP,
                split_mode='OFF')
            model = io_utils.join_meshes()  # OBJs often come in many many pieces
            bpy.context.scene.objects.active = model

            engine = 'BI'
            semantically_annotate_mesh(engine, model, view_dict)

            # model.show_transparent = True

            # render + save
            setup_and_render_image(TASK_NAME, basepath,
                                    clean_up=True,
                                    execute_render_fn=render_semantic_img,
                                    logger=None,
                                    view_dict=view_dict,
                                    view_number=view_number)

        if point_number > 30:
            break


'''
    SEMANTICS
'''


def add_materials_to_mesh(materials_dict, mesh):
    bpy.context.scene.objects.active = mesh
    materials_idxs = {} 
    for label, mat in materials_dict.items():
        bpy.ops.object.material_slot_add()
        mesh.material_slots[-1].material = mat
        materials_idxs[label] = len(mesh.material_slots) - 1
    return materials_dict, materials_idxs


def build_colormap(objects, point_info):
    objects = list(point_info['objects'].keys())
    objects.append('Ground_Mesh')

    class_to_instance = defaultdict(list)
    colors_dict = {}
    for i, obj in enumerate(objects):
        
        if obj == 'Ground_Mesh':
            r, g, b = 1., 1., 1.

        else:
            
            obj_info = point_info['objects'][obj]
            shape, size, material, color = obj_info['shape'], obj_info['size'], obj_info['material'], obj_info['color']
            shape_id = shapes.index(shape)
            size_id = sizes.index(size)
            material_id = materials.index(material)
            color_id = colors.index(color)

            class_ = (shape_id, size_id, color_id, material_id)

            if obj not in class_to_instance[class_]:
                class_to_instance[class_].append(obj)

            idx = class_to_instance[class_].index(obj)

            #########
            # obj_code = color_id + 8 * shape_id + (8 ** 2) * size_id + (8 ** 3) * material_id + (8 ** 4) * idx
            # dif = (255 ** 3) // (8 ** 5)
            # r = ((obj_code * dif) % 256) / 255.
            # g = (((obj_code * dif) >> 8) % 256) / 255.
            # b = (((obj_code * dif) >> 16) % 256) / 255.
            #########

            r = (shape_id + 10 * size_id) / 255.
            g = (color_id + 10 * material_id) / 255.
            b = idx / 255.


        colors_dict[obj] = np.array([r, g, b])

    def get_color(obj):
        return colors_dict[obj]

    return get_color


def build_materials_dict(engine, objects, point_info):
    '''
    Args:
        colormap: A function that returns a color for a semantic label

    Returns:
        materials_dict: A dict: materials_dict[ class ][ instance_num ] -> material

    '''
    colormap = build_colormap(objects, point_info)
    materials_dict = {}
    for i, obj in enumerate(objects):
        materials_dict[obj] = utils.create_material_with_color(colormap(obj), name=obj,
                                                                       engine=engine)
    return materials_dict


def semantically_annotate_mesh(engine, mesh, point_info):
    
    with Profiler("Read semantic annotations") as prf:
        face_to_object, objects = get_face_semantics(point_info)
        print("Number of labeled faces : {} ".format(len(face_to_object.keys())))


    materials_dict = build_materials_dict(engine, objects, point_info)

    # create materials
    with Profiler('Create materials on mesh'):
        _, materials_idxs = add_materials_to_mesh(materials_dict, mesh)

    bpy.context.scene.objects.active = mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh.data)
    bm.select_mode = {'FACE'}  # Go to face selection mode

    # Deselect all faces
    for face in bm.faces:
        face.select_set(False)
    mesh.data.update()
    bm.faces.ensure_lookup_table()

    
    with Profiler("Applying materials") as prf:
        # Count the votes and apply materials
        for i, face in enumerate(bm.faces):  # Iterate over all of the object's faces
            face_vertices = tuple(sorted([v.index for v in face.verts]))    
            if face_vertices not in face_to_object.keys():
                print("wtffffff")
                continue
            label = face_to_object[face_vertices]
            face.material_index = materials_idxs[str(label)]  # Assing random material to face

        mesh.data.update()
        bpy.ops.object.mode_set(mode='OBJECT')


'''
    RENDER
'''


def render_semantic_img(scene, save_path):
    """
      Renders an image from the POV of the camera and save it out

      Args:
        camera: A Blender camera already pointed in the right direction
        camera_data:
        scene: A Blender scene that the camera will render
        save_path: Where to save the image
        model: The model in context after loading the .ply
        view_dict: The loaded view dict from point_uuid.json
    """
    save_path_dir, img_filename = os.path.split(save_path)
    with Profiler("Render") as prf:
        utils.set_preset_render_settings(scene, presets=['BASE', 'NON-COLOR'])
        render_save_path = setup_scene_for_semantic_render(scene, save_path_dir)
        prf.step("Setup")

        bpy.ops.render.render()
        prf.step("Render")

    with Profiler("Saving") as prf:
        shutil.move(render_save_path, save_path)


def setup_scene_for_semantic_render(scene, outdir):
    """
      Creates the scene so that a depth image will be saved.

      Args:
        scene: The scene that will be rendered
        camera: The main camera that will take the view
        model: The main model
        outdir: The directory to save raw renders to

      Returns:
        save_path: The path to which the image will be saved
    """
    # Use node rendering for python control
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links

    # Make sure there are no existing nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    #  Set up a renderlayer and plug it into our remapping layer
    inp = tree.nodes.new('CompositorNodeRLayers')

    if (bpy.app.version[1] >= 70):  # Don't apply color transformation -- changed in Blender 2.70
        scene.view_settings.view_transform = 'Raw'
        scene.sequencer_colorspace_settings.name = 'Non-Color'

    # Save it out
    if outdir:
        out = tree.nodes.new('CompositorNodeOutputFile')
        ident = str(uu.uuid4())
        out.file_slots[0].path = ident
        out.base_path = outdir
        out.format.color_mode = 'RGB'

        out.format.color_depth = settings.COLOR_BITS_PER_CHANNEL
        out.format.file_format = settings.PREFERRED_IMG_EXT.upper()
        links.new(inp.outputs[0], out.inputs[0])
        ext = utils.img_format_to_ext[settings.PREFERRED_IMG_EXT.lower()]
        temp_filename = "{0}0001.{1}".format(ident, ext)
        return os.path.join(outdir, temp_filename)
    else:
        out = tree.nodes.new('CompositorNodeComposite')
        links.new(inp.outputs[0], out.inputs[0])
        return None


if __name__ == '__main__':
    with Profiler("create_semantic_images.py"):
        main()
