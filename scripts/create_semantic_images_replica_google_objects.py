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
from collections import defaultdict
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
task_name = 'semantic'
logger = settings.LOGGER


def make_settings():
    habitat_settings = default_sim_settings.copy()
    habitat_settings["width"] = 512
    habitat_settings["height"] = 512
    habitat_settings["scene"] = os.path.join(basepath, '../habitat/', settings.MODEL_FILE)
    habitat_settings["sensor_height"] = 0
    habitat_settings["color_sensor"] = False
    habitat_settings["semantic_sensor"] = True
    habitat_settings["seed"] = 1
    return habitat_settings


class Sim:
    def __init__(self, sim_settings):
        self.set_sim_settings(sim_settings)
        self.obj_id_to_num_instance = {}
        self.obj_id_to_num_instance = defaultdict(lambda: 0, self.obj_id_to_num_instance)
        with open(os.path.join(basepath, '../habitat/info_semantic.json')) as f:
            self.sem_info = json.load(f)
        self.get_semantic_info()


    def get_semantic_info(self):
        self.id_to_class = [0 if (cl==-1 or cl==-2) else cl for cl in self.sem_info['id_to_label']]
        self.id_to_instance = {}
        class_to_num_instance = {}
        class_to_num_instance = defaultdict(lambda: 0, class_to_num_instance)
        for id in range(len(self.sem_info['id_to_label'])):
            cl = self.id_to_class[id]
            if cl == 0:
                self.id_to_instance[id] = 0
            else:
                self.id_to_instance[id] = class_to_num_instance[cl]
                class_to_num_instance[cl] += 1

        self.MAX_SEMANTIC_ID = len(self.sem_info['id_to_label'])

    def set_sim_settings(self, sim_settings):
        self._sim_settings = sim_settings.copy()


    def save_semantic_observation(self, obs, save_path):
        semantic_obs = obs["semantic_sensor"]
        
        temp = np.expand_dims(semantic_obs, axis=2)
        semantic_img = np.concatenate([temp, temp, temp], axis=2)
        for id in np.unique(semantic_obs):
            if id >= self.MAX_SEMANTIC_ID: # google objects
                semantic_id = 102 + (id - self.MAX_SEMANTIC_ID) % len(self.objects)
                instance_id = (id - self.MAX_SEMANTIC_ID) // len(self.objects)
            else: # replica scene
                semantic_id = self.id_to_class[id]
                instance_id = self.id_to_instance[id]

            r = (semantic_id >> 8) % 265
            g = (semantic_id & 255) % 256 
            b = instance_id
            semantic_img[:,:,0][semantic_obs == id] = r
            semantic_img[:,:,1][semantic_obs == id] = g
            semantic_img[:,:,2][semantic_obs == id] = b

            
        semantic_rgb_img = Image.fromarray(np.uint8(semantic_img))
        semantic_rgb_img.save(save_path, quality=100)


    def init_common(self, fov):
        self._cfg = make_cfg(self._sim_settings, fov)
        scene_file = self._sim_settings["scene"]
        # create a simulator (Simulator python class object, not the backend simulator)

        try:
            self._sim = habitat_sim.Simulator(self._cfg)
        except Exception as err:
            print(err)
            traceback.print_exc()

        random.seed(self._sim_settings["seed"])
        self._sim.seed(self._sim_settings["seed"])
        # initialize the agent at a random start state
        agent = self._sim.initialize_agent(self._sim_settings["default_agent"])


    def create_semantic_images(self, view_dict):
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
        self.save_semantic_observation(observations, save_path)


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


    def add_objects(self):
        sim = self._sim
        obj_mgr = sim.get_object_template_manager()
        obj_mgr.load_configs("/scratch-data/ainaz/habitat-sim/data/objects/", True)
        assert obj_mgr.get_num_templates() > 0

        obj_list_file = os.path.join('/scratch-data/ainaz/Google_Objects/list_of_objects.json')
        with open(obj_list_file, encoding='utf-8') as f:
            self.objects = json.load(f)

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

            # add semantic id for the object
            obj_id = self.objects.index(obj_name)
            semantic_id = self.MAX_SEMANTIC_ID + \
                len(self.objects) * self.obj_id_to_num_instance[obj_id] + obj_id

            self.obj_id_to_num_instance[obj_id] += 1
            sim.set_object_semantic_id(semantic_id, id)





def main():
    habitat_settings = make_settings()

    point_infos = io_utils.load_saved_points_of_interest(basepath)

    sim = Sim(habitat_settings)
    sim.init_common(90)

    sim.add_objects()

    for point_number, point_info in enumerate(point_infos):
        for view_number, view_dict in enumerate(point_info):
            sim.create_semantic_images(view_dict)

    max_semantic_id = sim.MAX_SEMANTIC_ID
    sim._sim.close()
    del sim._sim
    print("!!!! MAX SEMANTIC ID : ", max_semantic_id)




if __name__ == "__main__":
    main()





