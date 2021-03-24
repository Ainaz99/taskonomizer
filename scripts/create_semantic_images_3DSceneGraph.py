"""
  Name: create_rgb_images.py
  Author: Sasha Sax, CVGL
  Desc: Creates RGB images of points in the points/ directory. Currently creates
    fixated, nonfixated.

  Usage:
    blender -b -noaudio --enable-autoexec --python create_rgb_images.py --
  
  Requires (to be run):
    - generate_points.py
"""

import bpy
import math
from mathutils import Vector, Euler
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from load_settings import settings
from create_images_utils import get_number_imgs
from load_3DSceneGraph_semantics import *
import io_utils
import utils
from utils import Profiler

ORIGIN = (0.0, 0.0, 0.0)
DEFAULT_ROTATION_FOR_INITIAL_SKYBOX = Euler((0, 0, 0),
                                            settings.EULER_ROTATION_ORDER)  # ( math.pi / 2, 0, math.pi / 2 ) for 'XYZ' ordering
DEFAULT_ROTATION_FOR_INITIAL_SKYBOX.rotate_axis('Z', math.pi / 2)
DEFAULT_ROTATION_FOR_INITIAL_SKYBOX.rotate_axis('X', math.pi / 2)
TASK = "segment_semantic"

CUBE_SIZE = 1.0  # Sasha: I think this shouldn't matter

gibson_data_path = "/scratch-data/ainaz/gibson_medium"
taskonomy_v2_path = "/scratch-data/ainaz/taskonomydata_v2"
base_path = os.path.join(taskonomy_v2_path, 'medium_split2')
camera_pose_path = os.path.join(gibson_data_path, settings.MODEL_NAME, settings.CAMERA_POSE_FILE)
semantic_skybox_path = os.path.join(base_path, settings.MODEL_NAME.lower() + '_semantic_skyboxes', 'semantic_skyboxes')
point_path = os.path.join(taskonomy_v2_path, 'points', settings.MODEL_NAME.lower() + '_point_info')


utils.set_random_seed()


def main():
    global logger
    logger = io_utils.create_logger(__name__)
    utils.delete_all_objects_in_context()

    # Create the cube
    create_cube(radius=CUBE_SIZE, location=ORIGIN)
    obj = bpy.context.object
    mesh = obj.data
    scene = bpy.context.scene

    camera_poses = io_utils.collect_camera_poses_from_csvfile(camera_pose_path)

    # Load points
    point_infos = io_utils.load_saved_points_of_interest(point_path)

    # Render engine alway cycles here
    scene.render.engine = 'CYCLES'

    n_images = get_number_imgs(point_infos)

    image_number = 1
    with Profiler("Render", logger=logger) as pflr:
        for point_number, point_info in enumerate(point_infos):
            for view_num, view_of_point in enumerate(point_info):

                camera, camera_data, _ = utils.get_or_create_camera(ORIGIN,
                                                                    rotation=DEFAULT_ROTATION_FOR_INITIAL_SKYBOX,
                                                                    field_of_view=view_of_point["field_of_view_rads"])
                initial_camera_rotation_in_real_world = Euler(view_of_point['camera_rotation_original'],
                                                              settings.EULER_ROTATION_ORDER)
                rgb_cube_model_offset = utils.get_euler_rotation_between(
                    initial_camera_rotation_in_real_world,
                    DEFAULT_ROTATION_FOR_INITIAL_SKYBOX)

                camera_uuid = None
                for key, value in camera_poses.items():
                    if list(value['position']) == view_of_point['camera_location']:
                        camera_uuid = key
                flag = False
                for img_name in os.listdir(semantic_skybox_path):
                    if img_name.startswith(camera_uuid):
                        flag = True
                        break
                if not flag:
                    print("!! Panorama {} does not exist!".format(camera_uuid))
                    continue

                wrap_material_around_cube(camera_uuid, mesh, semantic_skybox_path, ".png")

                if settings.CREATE_PANOS:
                    utils.make_camera_data_pano(camera_data)
                    save_path = io_utils.get_file_name_for(
                        dir=os.path.join(base_path, 'pano', TASK),
                        point_uuid=view_of_point["camera_uuid"],
                        view_number=settings.PANO_VIEW_NAME,
                        camera_uuid=view_of_point["camera_uuid"],
                        task=TASK,
                        ext=io_utils.img_format_to_ext[settings.PREFERRED_IMG_EXT.lower()])
                    set_render_settings(scene, save_path)
                    quiet_render(image_number, n_images, pflr)
                    image_number += 1
                    break  # Only want one pano/sweep

                if settings.CREATE_FIXATED:  # Render fixated image
                    # Point camera at correct location
                    # Aim camera at target by rotating a known amount
                    camera.rotation_euler = initial_camera_rotation_in_real_world
                    camera.rotation_euler.rotate(
                        Euler(view_of_point['camera_rotation_from_original_to_final'], settings.EULER_ROTATION_ORDER))
                    camera.rotation_euler.rotate(rgb_cube_model_offset)

                    # Render the image
                    rgb_render_path = io_utils.get_file_name_for(
                        dir=os.path.join(base_path, settings.MODEL_NAME.lower() + '_' + TASK, TASK),
                        point_uuid=view_of_point["point_uuid"],
                        view_number=view_num,
                        camera_uuid=view_of_point["camera_uuid"],
                        task=TASK,  # + "_fixated",
                        ext=io_utils.img_format_to_ext[settings.PREFERRED_IMG_EXT.lower()])
                    set_render_settings(scene, rgb_render_path)
                    quiet_render(image_number, n_images, pflr)
                    image_number += 1

                utils.delete_objects_starting_with("Camera")  # Clean up


# ------------------------------------------
#  Copied from original
# ------------------------------------------
def _legacy_point_camera_at_target():
    """ Do not use this method for pointing a camera at the target. It will point the
      camera in the right direction, but Blender forces an axis to point in the global
      'up' direction which may not align with the camera's initial up direction. If 
      the two do not align, then the aimed camera will be rotated from the correct 
      camera extrinsics. This will cause reconstruction error down the line.

      The legacy code is here for reference ONLY. 
    """

    pass


def verts_from_three_to_two(vertices):
    """ By Farhan """
    first_vert = vertices[0]
    if all(v[0] == first_vert[0] for v in vertices):
        return (0, first_vert[0])
    elif all(v[1] == first_vert[1] for v in vertices):
        return (1, first_vert[1])
    else:
        return (2, first_vert[2])


def translate_pixel_to_cube_verts(i, pixel_range, pixel_coords, locked_axis):
    """ By Farhan + Sasha """
    axis, value = locked_axis

    if i == 0 or i == 1:
        x_or_y = pixel_to_cube(pixel_range, (-CUBE_SIZE, CUBE_SIZE), pixel_coords[0])
        y_or_z = pixel_to_cube(pixel_range, (CUBE_SIZE, -CUBE_SIZE), pixel_coords[1])
    elif i == 2 or i == 3 or i == 4:
        x_or_y = pixel_to_cube(pixel_range, (CUBE_SIZE, -CUBE_SIZE), pixel_coords[0])
        y_or_z = pixel_to_cube(pixel_range, (CUBE_SIZE, -CUBE_SIZE), pixel_coords[1])
    else:
        x_or_y = pixel_to_cube(pixel_range, (-CUBE_SIZE, CUBE_SIZE), pixel_coords[0])
        y_or_z = pixel_to_cube(pixel_range, (CUBE_SIZE, -CUBE_SIZE), pixel_coords[1])

    if axis == 0:
        return (value, x_or_y, y_or_z)
    elif axis == 1:
        return (x_or_y, value, y_or_z)
    else:
        return (x_or_y, y_or_z, value)


def pixel_to_cube(old_range, new_range, pixel_coord):
    """ By Farhan """
    from_min, from_max = old_range
    to_min, to_max = new_range
    x = pixel_coord if to_max > to_min else from_max - pixel_coord
    new_range_len = abs(to_max - to_min)
    divisor = from_max / new_range_len
    return (x / divisor) - to_max if to_max > to_min else (x / divisor) - to_min


# ---------------------------------------------------------

def adjust_texture_mapping_for_face(tex_mapping, cube_face_idx):
    if cube_face_idx == 0:  # Front
        tex_mapping.mapping_x = 'Y'
        tex_mapping.mapping_y = 'X'
    elif cube_face_idx == 1:  # Right
        tex_mapping.mapping_x = 'Y'
        tex_mapping.mapping_y = 'X'
    elif cube_face_idx == 2:  # Back
        tex_mapping.mapping_x = 'Y'
        tex_mapping.mapping_y = 'X'
    elif cube_face_idx == 3:  # Left
        tex_mapping.mapping_x = 'Y'
        tex_mapping.mapping_y = 'X'
    elif cube_face_idx == 4:  # Bottom
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            tex_mapping.scale[1] = -1
    elif cube_face_idx == 5:  # Top
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            tex_mapping.scale[0] = -1
        else:
            pass


def create_cube(radius, location=ORIGIN):
    """
      Creates a cube at the origin
    """
    bpy.ops.mesh.primitive_cube_add(radius=radius, location=location, enter_editmode=True)
    bpy.ops.uv.unwrap()  # cube_project(cube_size=1.0/radius)
    bpy.ops.object.mode_set(mode='OBJECT')


def create_texture_from_img(filepath):
    """
      Creates a texture of the given image.

      Args:
        filepath: A string that contains the path to the Image

      Returns:
        texture: A texture that contains the given Image
    """
    texture = bpy.data.textures.new("ImageTexture", type='IMAGE')
    img = bpy.data.images.load(filepath)
    texture.image = img
    # To bleed the img over the seams
    texture.extension = 'EXTEND'
    # For sharp edges
    texture.use_mipmap = False
    texture.use_interpolation = False
    #   texture.filter_type = 'BOX'
    texture.filter_size = 0.80
    return texture


def get_or_create_image_material(uuid, img_dir, ext, cube_face_idx):
    img_idx = utils.cube_face_idx_to_skybox_img_idx[cube_face_idx]
    material_name = "Mat_{0}_{1}".format(uuid, img_idx)
    img_path = os.path.join(img_dir, uuid + "_semantic_skybox" + str(img_idx) + ext)
    if material_name in bpy.data.materials:
        return bpy.data.materials[material_name]
    else:
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            texture = create_texture_from_img(img_path)
            # To appear in a render, the image must be a texture which is on a material which applied to a face
            material = utils.create_material_with_texture(texture, name=material_name)
            # adjust_material_for_face( material, cube_face_idx )
            adjust_texture_mapping_for_face(material.texture_slots[0], cube_face_idx)
        elif bpy.context.scene.render.engine == 'CYCLES':
            # Create material
            material = bpy.data.materials.new(material_name)
            material.use_nodes = True
            tree = material.node_tree
            links = tree.links

            # Make sure there are no existing nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            nodes = tree.nodes
            inp = nodes.new(type="ShaderNodeTexCoord")

            # Set img as texture
            tex = nodes.new(type="ShaderNodeTexImage")
            tex.image = bpy.data.images.load(img_path)
            tex.extension = 'EXTEND'
            tex.interpolation = 'Closest'

            # Adjust the faces (using increasingly convoluted methods)
            if cube_face_idx == 4:
                links.new(inp.outputs[0], tex.inputs[0])
            elif cube_face_idx == 5:
                obj = bpy.context.object
                mesh = obj.data
                for face_idx, face in enumerate(mesh.polygons):
                    if face_idx != cube_face_idx: continue
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        uv_coords = mesh.uv_layers.active.data[loop_idx].uv
                        if vert_idx == 1:
                            uv_coords.x = 0
                            uv_coords.y = 1
                        elif vert_idx == 3:
                            uv_coords.x = 0
                            uv_coords.y = 0
                        elif vert_idx == 5:
                            uv_coords.x = 1
                            uv_coords.y = 1
                        elif vert_idx == 7:
                            uv_coords.x = 1
                            uv_coords.y = 0
            else:
                adjust_texture_mapping_for_face(tex.texture_mapping, cube_face_idx)

            # Make the material emit the image (so it's visible in render)
            emit_node = nodes.new("ShaderNodeEmission")
            links.new(tex.outputs[0], emit_node.inputs[0])

            # Now output that img
            out_node = nodes.new("ShaderNodeOutputMaterial")
            links.new(emit_node.outputs[0], out_node.inputs[0])
    return material


def set_render_settings(scene, rgb_render_path):
    """
      Sets the render settings for speed.

      Args:
        scene: The scene to be rendered
    """
    utils.set_preset_render_settings(scene, presets=['BASE'])
    render = scene.render
    render.layers["RenderLayer"].use_solid = True
    render.layers["RenderLayer"].use_halo = False
    render.layers["RenderLayer"].use_all_z = False
    render.layers["RenderLayer"].use_ztransp = False
    render.layers["RenderLayer"].use_sky = False
    render.layers["RenderLayer"].use_edge_enhance = False
    render.layers["RenderLayer"].use_strand = False
    render.layers["RenderLayer"].use_pass_z = False

    # Quality settings
    scene.render.resolution_percentage = 100
    scene.render.tile_x = settings.TILE_SIZE
    scene.render.tile_y = settings.TILE_SIZE
    scene.render.filepath = rgb_render_path
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = settings.COLOR_BITS_PER_CHANNEL
    scene.render.image_settings.file_format = settings.PREFERRED_IMG_EXT.upper()


def wrap_material_around_cube(uuid, mesh, img_dir, ext):
    """
      This will create images on the inside of the cube that correspond to the skybox images in the model.

      Args:
        uuid: A string that contains the uuid of the skybox
        mesh: The Blender mesh for the cube.
        img_dir: A string that contains the dir where {uuid}_skybox{i}.{ext} can be found
        ext: The ext for skybox images. In our case, .jpg

    """
    cube = bpy.data.objects["Cube"]

    # We need to make the cube the active object so that we can add materials
    bpy.context.scene.objects.active = cube
    while len(cube.material_slots) < 6:
        bpy.ops.object.material_slot_add()

    # bpy.ops.object.mode_set(mode='OBJECT')
    for cube_face_idx, f in enumerate(mesh.polygons):
        material = get_or_create_image_material(uuid, img_dir, ext, cube_face_idx)
        cube.material_slots[cube_face_idx].material = material
        f.material_index = cube_face_idx


def quiet_render(img_number, n_images, pflr):
    # redirect output to log file
    logfile = 'blender_render.log'
    open(logfile, 'a').close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)

    # do the rendering
    bpy.ops.render.render(write_still=True)
    pflr.step('finished img {}/{}'.format(img_number, n_images))

    # disable output redirection
    os.close(1)
    os.dup(old)
    os.close(old)
    try:
        os.remove(logfile)
    except:
        pass


if __name__ == "__main__":
    with Profiler("create_rgb_images.py"):
        main()
