import argparse
import math
import multiprocessing
import os
import traceback
import glob
from natsort import natsorted
import random
import json
import pickle
from itertools import groupby
import time
from enum import Enum
import numpy as np
from PIL import Image
from mathutils import Vector, Euler
import magnum as mn
import habitat_sim
import habitat_sim.agent
from habitat_sim import bindings as hsim
from pytransform3d.rotations import *
from scipy.spatial.transform import Rotation as R

from habitat_settings import default_sim_settings, make_cfg, make_agent_cfg
import io_utils
from create_images_utils import *
from load_settings import settings


basepath = settings.MODEL_PATH
task_name = 'rgb'
logger = settings.LOGGER

def make_settings():
    habitat_settings = default_sim_settings.copy()
    habitat_settings["width"] = 512
    habitat_settings["height"] = 512
    habitat_settings["scene"] = os.path.join(basepath, '..', settings.MODEL_FILE)
    habitat_settings["sensor_height"] = 0
    habitat_settings["color_sensor"] = True
    habitat_settings["seed"] = 1
    return habitat_settings


class Sim:
    def __init__(self, sim_settings):
        self.set_sim_settings(sim_settings)


    def set_sim_settings(self, sim_settings):
        self._sim_settings = sim_settings.copy()


    def save_color_observation(self, obs, save_path):
        color_obs = obs["color_sensor"]
        color_rgba_img = Image.fromarray(color_obs, mode="RGBA")
        color_rgb_img = Image.new("RGB", color_rgba_img.size, (255, 255, 255))
        color_rgb_img.paste(color_rgba_img, mask=color_rgba_img.split()[3])
        color_rgb_img.save(save_path, quality=100)


    def init_common(self, fov):
        print("------------------- version : ", habitat_sim.__version__)
        self._cfg = make_cfg(self._sim_settings, fov)
        scene_file = self._sim_settings["scene"]
        # create a simulator (Simulator python class object, not the backend simulator)

        print("!!!!!!!!!!!!!!!!!! before simulator")
        try:
            self._sim = habitat_sim.Simulator(self._cfg)
        except Exception as err:
            print(err)
            traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!! after simulator")

        random.seed(self._sim_settings["seed"])
        self._sim.seed(self._sim_settings["seed"])
        # initialize the agent at a random start state
        agent = self._sim.initialize_agent(self._sim_settings["default_agent"])

        stage_attr_mgr = self._sim.get_stage_template_manager()
        template = stage_attr_mgr.get_template_handle_by_ID(0)
        print("********************* ", template)


    def create_rgb_images(self, view_dict):
        pos = view_dict['camera_location']
        rot = view_dict['camera_rotation_final_quaternion']
        point_uuid = view_dict['point_uuid']
        camera_uuid = view_dict['camera_uuid']
        fov = view_dict['field_of_view_rads']
        view_id = view_dict['view_id']

        self._cfg = make_cfg(self._sim_settings, fov * 180 / np.pi)
        self._sim.reconfigure(self._cfg)
        agent = self._sim.initialize_agent(self._sim_settings["default_agent"])
        print("fov = ", self._sim.get_agent(0).agent_config.sensor_specifications[0].parameters.__getitem__('hfov'))

        start_state = agent.get_state()
        new_pos = [pos[0], pos[2], -pos[1]]
        start_state.position = new_pos

        R1 = matrix_from_quaternion(rot)
        R_trans = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        R2 = R_trans.dot(R1)
        quat_rot = quaternion_from_matrix(R2)

        start_state.rotation = np.quaternion(quat_rot[0], quat_rot[1], quat_rot[2], quat_rot[3])
        agent.set_state(start_state)
        print(
            "start_state.position\t",
            start_state.position,
            "start_state.rotation\t",
            start_state.rotation,
        )
        observations = self._sim.get_sensor_observations()
        save_path = io_utils.get_file_name_for(
            dir=get_save_dir(basepath, task_name),
            point_uuid=point_uuid,
            view_number=view_id,
            camera_uuid=camera_uuid,
            task=task_name,
            ext='png')
        self.save_color_observation(observations, save_path)


    def simulate(self, dt=1.0, get_frames=False):
        sim=self._sim
        # simulate dt seconds at 60Hz to the nearest fixed timestep
        print("Simulating " + str(dt) + " world seconds.")
        observations = []
        start_time = sim.get_world_time()
        print("------------ start time : ", start_time)
        while sim.get_world_time() < start_time + dt:
            print("----------- world time : ", sim.get_world_time())
            try:
                sim.step_physics(1 / 60.0)
            except Exception as err:
                print(err)
                traceback.print_exc()
            # if get_frames:
            #     observations.append(sim.get_sensor_observations())
        return observations


    def get_template_handles(self, obj_mgr, obj_name, is_goole_obj=True):
        if is_goole_obj: 
            return obj_mgr.get_template_handles("data/objects/google_objects/{}".format(obj_name))
        return obj_mgr.get_template_handles("data/objects/{}".format(obj_name))


    def drop_objects(self):
        sim = self._sim
        scene_bb = sim.pathfinder.get_bounds()  # scene bounding box
        min_bound, max_bound = scene_bb[0], scene_bb[1]
        area = (max_bound[0] - min_bound[0]) * (max_bound[2] - min_bound[2])
        count = int(settings.OBJ_DENSITY * area * 1.7)  
        obj_mgr = sim.get_object_template_manager()
        
        obj_mgr.load_configs("/scratch-data/ainaz/habitat-sim/data/objects/", True)
        assert obj_mgr.get_num_templates() > 0

        obj_list_file = os.path.join('/scratch-data/ainaz/Google_Objects/list_of_objects.json')
        with open(obj_list_file, encoding='utf-8') as f:
            objects = json.load(f)
        print("Total number of objects : ", len(objects))
        objID_to_name = {}
        obj_id = 0

        while obj_id < count:
            obj_name = objects[random.randint(0, len(objects) - 1)]

            is_google_obj = False if obj_name in ['banana', 'cheezit', 'chefcan'] else True
            id = sim.add_object_by_handle(
                self.get_template_handles(obj_mgr, obj_name, is_goole_obj=is_google_obj)[0])

            # object bounding box
            obj_bbox = sim.get_object_visual_scene_nodes(id)[0].cumulative_bb
            # object height calculated from origin
            obj_dim = 0 - min(obj_bbox.x().min, obj_bbox.y().min, obj_bbox.z().min)
            obj_h = 0 - obj_bbox.y().min
            print("Obj bbox: ", obj_bbox, "Obj height: ", obj_h, "Obj name: ", obj_name)

            # random initial position for object
            x = np.random.uniform(min_bound[0], max_bound[0])

            # y = min_bound[1] + 2
            rand = random.random()
            if rand < 0.6: y = min_bound[1] + 2
            else: y = min_bound[1] + 4

            z = np.random.uniform(min_bound[2], max_bound[2])

            # cast a ray from right below the object along the y axis
            center_ray = habitat_sim.geo.Ray(Vector([x, y - obj_h, z]), Vector([0,-1,0]))
            raycast_results = sim.cast_ray(center_ray, max_distance=100)
            closest_dist = 1000.0   # closest distance from below the object to the surface
            if raycast_results.has_hits():
                for hit in raycast_results.hits:
                    if hit.ray_distance < closest_dist:
                        closest_dist = hit.ray_distance

            print("closest distance: ", closest_dist)
            if closest_dist == 1000: 
                sim.remove_object(obj_id)
                continue

            objID_to_name[obj_id] = obj_name
            obj_id += 1

            new_trans = np.array(
                [x, y - (closest_dist + obj_h) + 1.5 * obj_dim, z]) # drop from 1.2 * object height above the surface
            sim.set_translation(new_trans, id)

            random_rot = R.random().as_quat() # scalar-last format
            rot = mn.Quaternion(mn.Vector3(random_rot[0], random_rot[1], random_rot[2]), mn.Rad(random_rot[3]))
            sim.set_rotation(rot, id)

        print("************* ", obj_id)

        # simulate
        observations = self.simulate(dt=2, get_frames=False)

        existing_object_ids = self._sim.get_existing_object_ids()
        agent = self._sim.get_agent(0)
        objs_habitat = []
        objs_blender = []
        for obj_id in existing_object_ids:
            # obj_name = objects[obj_id // n]
            obj_name = objID_to_name[obj_id]
            print(obj_id)

            try:
                pos = self._sim.get_translation(obj_id)
                rot = self._sim.get_rotation(obj_id)

                # Check if object is in scene bounding box
                if pos[0] > max_bound[0] - 0.2 or pos[0] < min_bound[0] + 0.2: continue
                if pos[1] > max_bound[1] - 0.2 or pos[1] < min_bound[1]      : continue
                if pos[2] > max_bound[2] - 0.2 or pos[2] < min_bound[2] + 0.2: continue

                blender_pos = np.array([pos[0], -pos[2], pos[1]])
                R1 = rot.to_matrix()
                R_trans = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
                R2 = R_trans.dot(R1)
                blender_rot_quat = quaternion_from_matrix(R2)
                blender_rot = euler_xyz_from_matrix(R2)

                objs_habitat.append([np.array(pos), np.array(rot.vector), rot.scalar, obj_name])
                objs_blender.append([blender_pos, blender_rot, blender_rot_quat, obj_name])

            except:
                print("Failed! Some problem with rotation matrix...")
        
        with open(os.path.join(settings.MODEL_PATH, 'objs_habitat.pkl'), 'wb') as f:
            pickle.dump(objs_habitat, f)
        with open(os.path.join(settings.MODEL_PATH, 'objs_blender.pkl'), 'wb') as f:
            pickle.dump(objs_blender, f)



    def add_objects(self):
        sim = self._sim
        obj_mgr = sim.get_object_template_manager()
        obj_mgr.load_configs("/scratch-data/ainaz/habitat-sim/data/objects/", True)
        assert obj_mgr.get_num_templates() > 0

        with open(os.path.join(basepath, 'objs_habitat.pkl'), 'rb') as f:
            objs = pickle.load(f)

        for obj_info in objs:
            p, v, s, obj_name = obj_info[0], obj_info[1], obj_info[2], obj_info[3]
            is_google_obj = False if obj_name in ['banana', 'cheezit', 'chefcan'] else True
            id = sim.add_object_by_handle(
                self.get_template_handles(obj_mgr, obj_name, is_goole_obj=is_google_obj)[0])
            
            sim.set_translation(mn.Vector3(p), id)

            rot = mn.Quaternion(mn.Vector3(v[0], v[1], v[2]), mn.Rad(s))
            sim.set_rotation(rot, id)
            sim.set_object_motion_type(habitat_sim.physics.MotionType.STATIC , id)




def main():
    habitat_settings = make_settings()

    point_infos = io_utils.load_saved_points_of_interest(basepath)

    sim = Sim(habitat_settings)
    sim.init_common(90)

    sim.drop_objects() 

    # sim.add_objects()
    # for point_number, point_info in enumerate(point_infos):
    #     for view_number, view_dict in enumerate(point_info):
    #         sim.create_rgb_images(view_dict)

    sim._sim.close()
    del sim._sim



if __name__ == "__main__":
    main()





