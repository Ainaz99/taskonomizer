from pylab import *

import argparse
import h5py
import glob
import os
import json
import PIL.ImageDraw
from scipy.spatial.transform import Rotation as R

parser = argparse.ArgumentParser()
parser.add_argument("--scene_dir", required=False)
parser.add_argument("--camera_name", required=False)
args = parser.parse_args()

args.camera_name = 'cam_00'
args.scene_dir = '/home/ainaz/Desktop/hypersim/ai_001_001'
base_path = '/home/ainaz/Desktop/hypersim/ai_001_001_mesh/_asset_export'
points_path = os.path.join(base_path, 'point_info')
os.makedirs(points_path, exist_ok=True)


images_dir = os.path.join(args.scene_dir, "images")
in_scene_fileroot    = "scene"
camera_keyframe_frame_indices_hdf5_file = os.path.join(args.scene_dir, "_detail", args.camera_name, "camera_keyframe_frame_indices.hdf5")
camera_keyframe_positions_hdf5_file     = os.path.join(args.scene_dir, "_detail", args.camera_name, "camera_keyframe_positions.hdf5")
camera_keyframe_orientations_hdf5_file  = os.path.join(args.scene_dir, "_detail", args.camera_name, "camera_keyframe_orientations.hdf5")
in_rgb_jpg_dir       = os.path.join(images_dir, in_scene_fileroot + "_" + args.camera_name + "_final_preview")
in_rgb_jpg_files     = os.path.join(images_dir, in_scene_fileroot + "_" + args.camera_name + "_final_preview", "frame.*.tonemap.jpg")
in_filenames = [ os.path.basename(f) for f in sort(glob.glob(in_rgb_jpg_files)) ]

with h5py.File(camera_keyframe_frame_indices_hdf5_file, "r") as f: camera_keyframe_frame_indices = f["dataset"][:]
with h5py.File(camera_keyframe_positions_hdf5_file,     "r") as f: camera_keyframe_positions     = f["dataset"][:]
with h5py.File(camera_keyframe_orientations_hdf5_file,  "r") as f: camera_keyframe_orientations  = f["dataset"][:]

# frame_id = 10
# in_filename = in_filenames[frame_id]

for in_filename in in_filenames:

    in_filename_ids = [int(t) for t in in_filename.split(".") if t.isdigit()]
    assert len(in_filename_ids) == 1
    frame_id = in_filename_ids[0]

    # get camera parameters
    keyframe_ids = where(camera_keyframe_frame_indices == frame_id)[0]
    assert len(keyframe_ids) == 1

    keyframe_id        = keyframe_ids[0]
    camera_position    = camera_keyframe_positions[keyframe_id] / 100
    camera_orientation = camera_keyframe_orientations[keyframe_id]


    print("camera_position : ", camera_position) 
    print("camera_orientation : ", camera_orientation)

    r = R.from_dcm(camera_orientation).as_euler('xyz', degrees=False)

    print("r : ", r)

    in_rgb_jpg_file       = os.path.join(in_rgb_jpg_dir, in_filename)
    rgb_color = imread(in_rgb_jpg_file)

    height_pixels = rgb_color.shape[0] 
    width_pixels  = rgb_color.shape[1]
    fov_x         = pi/3.0
    fov_y         = 2.0 * arctan(height_pixels * tan(fov_x/2.0) / width_pixels)

    print("h,w : ", height_pixels, width_pixels)
    print("fov : ", fov_x, fov_y)

    point_info = {}
    point_info['location'] = camera_position.tolist()
    point_info['rotation'] = r.tolist()
    point_info['fov_x'] = fov_x
    point_info['fov_y'] = fov_y
    point_info['height'] = height_pixels
    point_info['width'] = width_pixels

    file_name = 'point_{}_view_0_domain_point_info.json'.format(frame_id)
    with open(os.path.join(points_path, file_name), 'w') as outfile:
        json.dump(point_info, outfile)
