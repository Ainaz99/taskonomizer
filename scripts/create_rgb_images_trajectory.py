import math
import os
import random
import sys
import imageio
import magnum as mn
import json
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import habitat_sim
from pytransform3d.rotations import *
from habitat_sim.utils import common as utils
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
import quaternion
from habitat_sim.utils import viz_utils as vut
from load_settings import settings
from pytransform3d.rotations import *

TASK = 'rgb'
basepath = settings.MODEL_PATH
scene = os.path.join(basepath, 'mesh.ply')
save_path = os.path.join(basepath, TASK)
point_info_save_path = os.path.join(basepath, 'point_info')

rgb_sensor = True  # @param {type:"boolean"}
depth_sensor = True  # @param {type:"boolean"}
semantic_sensor = True  # @param {type:"boolean"}

seed = 4
sensor_height = 0.8
step_size = 0.05
num_samples = 6
height_diff = 0.4
rotation_coef = 50
min_distance = 3
rotate_degree = 10

sim_settings = {
    "width": 640,  # Spatial resolution of the observations
    "height": 480,
    "scene": scene,  # Scene path
    "default_agent": 0,
    "sensor_height": sensor_height,  # Height of sensors in meters
    "color_sensor": rgb_sensor,  # RGB sensor
    "depth_sensor": depth_sensor,  # Depth sensor
    "semantic_sensor": semantic_sensor,  # Semantic sensor
    "seed": 1,  # used in the random navigation
    "enable_physics": False,  # kinematics only
}


def display_sample(obs, ix, pos, rot):

    blender_pos = np.array([pos[0], -pos[2], (pos[1]+sensor_height)])
    # R1 = mn.Quaternion(mn.Vector3(rot.x, rot.y, rot.z), rot.w).to_matrix() 
    R1 = matrix_from_quaternion([rot.w, rot.x, rot.y, rot.z])
    R_trans = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

    R2 = R_trans.dot(R1)
    blender_rot_quat = quaternion_from_matrix(R2)
    blender_rot = euler_xyz_from_matrix(R2)

    d = {}
    d['camera_rotation_final_quaternion'] = list(blender_rot_quat.astype('float64'))
    d['camera_rotation_final'] = list(blender_rot.astype('float64'))
    d['camera_rotation_original'] = list(blender_rot.astype('float64'))
    d['camera_location'] = list(blender_pos.astype('float64'))
    d['field_of_view_rads'] = np.float64(np.pi / 2)
    d['point_uuid'], d['view_id'], d['camera_uuid'] = ix, 0, 0
    d['camera_rotation_from_original_to_final'] = [0., 0., 0.]

    with open(os.path.join(point_info_save_path, f'point_{ix}_view_0_domain_point_info.json'), 'w') as outfile:
        json.dump(d, outfile)

    color_obs = obs["color_sensor"]
    color_rgba_img = Image.fromarray(color_obs, mode="RGBA")

    color_rgb_img = Image.new("RGB", color_rgba_img.size, (255, 255, 255))
    color_rgb_img.paste(color_rgba_img, mask=color_rgba_img.split()[3])
    color_rgb_img.save(os.path.join(save_path, f"point_{ix}_view_0_domain_rgb.png"), quality=100)



def make_cfg(settings):
    sim_cfg = habitat_sim.SimulatorConfiguration()
    sim_cfg.gpu_device_id = 0
    sim_cfg.scene.id = settings["scene"]
    sim_cfg.enable_physics = settings["enable_physics"]

    # Note: all sensors must have the same resolution
    sensors = {
        "color_sensor": {
            "sensor_type": habitat_sim.SensorType.COLOR,
            "resolution": [settings["height"], settings["width"]],
            "position": [0.0, settings["sensor_height"], 0.0],
        },
        "depth_sensor": {
            "sensor_type": habitat_sim.SensorType.DEPTH,
            "resolution": [settings["height"], settings["width"]],
            "position": [0.0, settings["sensor_height"], 0.0],
        },
        "semantic_sensor": {
            "sensor_type": habitat_sim.SensorType.SEMANTIC,
            "resolution": [settings["height"], settings["width"]],
            "position": [0.0, settings["sensor_height"], 0.0],
        },
    }

    sensor_specs = []
    for sensor_uuid, sensor_params in sensors.items():
        if settings[sensor_uuid]:
            sensor_spec = habitat_sim.SensorSpec()
            sensor_spec.uuid = sensor_uuid
            sensor_spec.sensor_type = sensor_params["sensor_type"]
            sensor_spec.resolution = sensor_params["resolution"]
            sensor_spec.position = sensor_params["position"]

            sensor_specs.append(sensor_spec)

    # Here you can specify the amount of displacement in a forward action and the turn angle
    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = sensor_specs
    agent_cfg.action_space = {
        "move_forward": habitat_sim.agent.ActionSpec(
            "move_forward", habitat_sim.agent.ActuationSpec(amount=step_size)
        ),
        "turn_left": habitat_sim.agent.ActionSpec(
            "turn_left", habitat_sim.agent.ActuationSpec(amount=rotate_degree)
        ),
        "turn_right": habitat_sim.agent.ActionSpec(
            "turn_right", habitat_sim.agent.ActuationSpec(amount=rotate_degree)
        ),
    }

    return habitat_sim.Configuration(sim_cfg, [agent_cfg])


cfg = make_cfg(sim_settings)
# Needed to handle out of order cell run in Colab

sim = habitat_sim.Simulator(cfg)
# the navmesh can also be explicitly loaded
sim.pathfinder.load_nav_mesh(os.path.join(basepath, 'habitat', 'mesh_semantic.navmesh'))

# the randomness is needed when choosing the actions
random.seed(sim_settings["seed"])
sim.seed(sim_settings["seed"])

# Set agent state
agent = sim.initialize_agent(sim_settings["default_agent"])
agent_state = habitat_sim.AgentState()
agent_state.position = np.array([-0.6, 0.0, 0.0])  # world space
agent.set_state(agent_state)

# @markdown The shortest path between valid points on the NavMesh can be queried as shown in this example.


 # @param {type:"integer"}
sim.pathfinder.seed(seed)

# fmt off
# @markdown 1. Sample valid points on the NavMesh for agent spawn location and pathfinding goal.
# fmt on

frame_number = 0
sample_points = []
sample1 = sim.pathfinder.get_random_navigable_point()
sample_points.append(sample1)
agent_state = habitat_sim.AgentState()
print("!!!!!!!!! bounds : ", sim.pathfinder.get_bounds())
try1 = 0
while len(sample_points) < num_samples:
    try1 += 1
    if try1 > 100:
        break
    try2 = 0
    while True:
        try2 += 1
        if try2 > 100:
            break
        sample2 = sim.pathfinder.get_random_navigable_point()
        flag = True
        for sample in sample_points:
            path = habitat_sim.ShortestPath()
            path.requested_start = sample
            path.requested_end = sample2
            found_path = sim.pathfinder.find_path(path)
            if path.geodesic_distance < min_distance:
                flag = False
        if flag:
            break

    # @markdown 2. Use ShortestPath module to compute path between samples.
    path = habitat_sim.ShortestPath()
    path.requested_start = sample1
    path.requested_end = sample2
    found_path = sim.pathfinder.find_path(path)
    geodesic_distance = path.geodesic_distance
    path_points = path.points
    # @markdown - Success, geodesic path length, and 3D points can be queried.
    print("found_path : " + str(found_path))
    print("geodesic_distance : " + str(geodesic_distance))
    print("number of keypoints : ", len(path_points))

    # @markdown 3. Display trajectory (if found) on a topdown map of ground floor
    if abs(sample2[1] - sample1[1]) > height_diff:
        continue
    if found_path:
        sample_points.append(sample2)
        path_points.insert(0, agent_state.position)
        # @markdown 4. (optional) Place agent and render images at trajectory points (if found).

        print("Rendering observations at path points:")

        for ix, point in enumerate(path_points):
            if ix < len(path_points) - 1:

                tangent = path_points[ix + 1] - point
                if tangent[0] == 0 and tangent[1] == 0 and tangent[2] == 0:
                    continue
                agent_state.position = point

                tangent_orientation_matrix = mn.Matrix4.look_at(
                    point, point + tangent, np.array([0, 1.0, 0])
                )
                tangent_orientation_q = mn.Quaternion.from_matrix(
                    tangent_orientation_matrix.rotation()
                )

                #### Update rotation
                current_rotation = agent_state.rotation
                final_rotation = utils.quat_from_magnum(tangent_orientation_q)
                diff_rotation = final_rotation - current_rotation
                diff_rot_size = np.sqrt(diff_rotation.x ** 2 + diff_rotation.y ** 2
                                        + diff_rotation.z ** 2 + diff_rotation.w ** 2)
                num_step_rot = int(diff_rot_size * rotation_coef)
                print("rotation steps =  ", num_step_rot)

                if num_step_rot != 0:
                    cur_rot = np.array([current_rotation.w, current_rotation.x, current_rotation.y, current_rotation.z])
                    final_rot = np.array([final_rotation.w, final_rotation.x, final_rotation.y, final_rotation.z])
                    key_rots = R.from_quat([cur_rot, final_rot])
                    slerp = Slerp([0, num_step_rot], key_rots)
                    times = [i for i in range(num_step_rot)]
                    interp_rots = slerp(times).as_quat()
                    for rot in interp_rots:
                        observations = sim.get_sensor_observations()
                        display_sample(observations, frame_number, agent_state.position, agent_state.rotation)
                        frame_number += 1
                        new_rot = np.quaternion(rot[0], rot[1], rot[2], rot[3])
                        agent_state.rotation = new_rot
                        agent.set_state(agent_state)

                agent_state.rotation = final_rotation
                agent.set_state(agent_state)
                observations = sim.get_sensor_observations()
                display_sample(observations, frame_number, agent_state.position, agent_state.rotation)
                frame_number += 1

                ### Update position
                distance = np.sqrt(tangent[0] ** 2 + tangent[1] ** 2 + tangent[2] ** 2)
                num_step_pos = int(distance // step_size)
                print("position steps = ", num_step_pos)
                if num_step_pos != 0:
                    pos_step = tangent / num_step_pos

                    for i in range(num_step_pos):
                        new_position = agent_state.position + pos_step
                        agent_state.position = new_position
                        agent.set_state(agent_state)
                        observations = sim.get_sensor_observations()
                        display_sample(observations, frame_number, agent_state.position, agent_state.rotation)
                        frame_number += 1

    sample1 = sample2

print("Total number of frames = ", frame_number)
