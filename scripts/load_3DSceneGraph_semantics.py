import os
import numpy as np
from PIL import Image


class Building():
    def __init__(self):
        ''' Building 3D Scene Graph attributes '''
        self.floor_area = None  # 2D floor area in sq.meters
        self.function = None  # function of building
        self.gibson_split = None  # Gibson split (tiny, medium, large)
        self.id = None  # unique building id
        self.name = None  # name of gibson model
        self.num_cameras = None  # number of panoramic cameras in the model
        self.num_floors = None  # number of floors in the building
        self.num_objects = None  # number of objects in the building
        self.num_rooms = None  # number of rooms in the building
        self.reference_point = None  # building reference point
        self.size = np.zeros((3))  # 3D Size of building
        self.volume = None  # 3D volume of building computed from 3D convex hull (cubic meters)
        self.voxel_size = None  # size of voxel
        self.voxel_centers = None  # 3D coordinates of voxel centers (Nx3)
        self.voxel_resolution = None  # Number of voxels per axis (k x l x m)

        # instantiate other graph layers
        self.room = {}
        self.camera = {}
        self.object = {}

    def set_attribute(self, value, attribute):
        ''' Set a building attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown building attribute: {}'.format(attribute))
            return
        self.__dict__[attribute] = value

    def get_attribute(self, attribute):
        ''' Get a building attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown building attribute: {}'.format(attribute))
            return -1
        return self.__dict__[attribute]


class Room():
    def __init__(self):
        ''' Room 3D Scene Graph attributes '''
        self.floor_area = None  # 2D floor area in sq.meters
        self.floor_number = None  # index of floor that contains the space
        self.id = None  # unique space id per building
        self.location = np.empty((3))  # 3D coordinates of room center's location
        self.inst_segmentation = None  # building face inidices that correspond to this room
        self.scene_category = None  # function of this room
        self.size = np.empty((3))  # 3D Size of room
        self.voxel_occupancy = None  # building's voxel indices that correspond to this room
        self.volume = None  # 3D volume of room computed from 3D convex hull (cubic meters)
        self.parent_building = None  # parent building that contains this room

    def set_attribute(self, value, attribute):
        ''' Set a room attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown room attribute: {}'.format(attribute))
            return
        self.__dict__[attribute] = value

    def get_attribute(self, attribute):
        ''' Get a room attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown room attribute: {}'.format(attribute))
            return -1
        return self.__dict__[attribute]


class Object:
    def __init__(self):
        ''' Object 3D Scene Graph attributes '''
        self.action_affordance = None  # list of possible actions
        self.floor_area = None  # 2D floor area in sq.meters
        self.surface_coverage = None  # total surface coverage in sq.meters
        self.class_ = None  # object label
        self.id = None  # unique object id per building
        self.location = np.empty((3))  # 3D coordinates of object center's location
        self.material = None  # list of main object materials
        self.size = np.empty((3))  # 3D Size of object
        self.inst_segmentation = None  # building face inidices that correspond to this object
        self.tactile_texture = None  # main tactile texture (can be None)
        self.visual_texture = None  # main visible texture (can be None)
        self.volume = None  # 3D volume of object computed from 3D convex hull (cubic meters)
        self.voxel_occupancy = None  # building's voxel indices that correspond to this object
        self.parent_room = None  # parent room that contains this object

    def set_attribute(self, value, attribute):
        ''' Set an object attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown object attribute: {}'.format(attribute))
            return
        self.__dict__[attribute] = value

    def get_attribute(self, attribute):
        ''' Get an object attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown object attribute: {}'.format(attribute))
            return -1
        return self.__dict__[attribute]


class Camera():
    ''' Camera 3D Scene Graph attributes '''

    def __init__(self):
        self.name = None  # name of camera
        self.id = None  # unique camera id
        self.FOV = None  # camera field of view
        self.location = np.empty((3))  # 3D location of camera in the model
        self.rotation = np.empty((3))  # rotation of camera (quaternion)
        self.modality = None  # camera modality (e.g., RGB, grayscale, depth, etc.)
        self.resolution = np.empty((2))  # camera resolution
        self.parent_room = None  # parent room that contains this camera

    def set_attribute(self, value, attribute):
        ''' Set a camera attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown camera attribute: {}'.format(attribute))
            return
        self.__dict__[attribute] = value

    def get_attribute(self, attribute):
        ''' Get a camera attribute '''
        if attribute not in self.__dict__.keys():
            print('Unknown camera attribute: {}'.format(attribute))
            return -1
        return self.__dict__[attribute]


def load_file(npz_path, building):
    ''' Load 3D Scene Graph data in the npz files
        panoramas [output] : one numpy array with object instances and one with object classes
    '''
    data = np.load(npz_path, allow_pickle=True)['output'].item()

    # set bldg attributes
    for key in data['building'].keys():
        if key in ['object_inst_segmentation', 'room_inst_segmentation', 'object_voxel_occupancy',
                   'room_voxel_occupancy']:
            continue
        building.set_attribute(data['building'][key], key)
    res = building.voxel_resolution
    voxel_cents = np.reshape(building.voxel_centers, (res[0], res[1], res[2], 3))
    building.set_attribute(voxel_cents, 'voxel_centers')

    # set room attributes
    unique_rooms = np.unique(data['building']['room_inst_segmentation'])
    for room_id in unique_rooms:
        if room_id == 0:
            continue
        building.room[room_id] = Room()
        room_faces = np.where(data['building']['room_inst_segmentation'] == room_id)[0]
        building.room[room_id].set_attribute(room_faces, 'inst_segmentation')
        room_voxels = np.where(data['building']['room_voxel_occupancy'] == room_id)[0]
        building.room[room_id].set_attribute(room_voxels, 'voxel_occupancy')
        for key in data['room'][room_id].keys():
            building.room[room_id].set_attribute(data['room'][room_id][key], key)

    # set object attributes
    unique_objects = np.unique(data['building']['object_inst_segmentation'])
    for object_id in unique_objects:
        if object_id == 0:
            continue
        building.object[object_id] = Object()
        object_faces = np.where(data['building']['object_inst_segmentation'] == object_id)[0]
        building.object[object_id].set_attribute(object_faces, 'inst_segmentation')
        object_voxels = np.where(data['building']['object_voxel_occupancy'] == object_id)[0]
        building.object[object_id].set_attribute(object_voxels, 'voxel_occupancy')
        for key in data['object'][object_id].keys():
            building.object[object_id].set_attribute(data['object'][object_id][key], key)

    # set camera attributes
    for cam_id in data['camera'].keys():
        if cam_id == 0:
            continue
        building.camera[cam_id] = Camera()
        for key in data['camera'][cam_id].keys():
            building.camera[cam_id].set_attribute(data['camera'][cam_id][key], key)

    if 'panorama' in data.keys():
        panoramas = data['panorama']
    else:
        panoramas = None
        print('No panoramas in {}'.format(building.name))
    return building, panoramas


def load_3DSceneGraph(model, data_path):
    ''' Load 3D SceneGraph attributes 
        model: name of Gibson model
        data_path : location of folder with annotations
    '''
    building = Building()
    npz_path = os.path.join(data_path, '3DSceneGraph_' + model + '.npz')
    building, panoramas = load_file(npz_path, building)
    return building, panoramas


def get_coco_dataset():
    '''A dummy COCO dataset that includes only the 'classes' field.
    '''
    classes = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
        'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
        'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
        'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
        'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
        'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
        'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
        'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
        'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
        'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
        'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
        'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]

    # classes that won't be found indoors in the data
    not_indoor = ['person', 'airplane', 'street sign',
                  'bus', 'train', 'truck', 'traffic light', 'fire hydrant',
                  'stop sign', 'parking meter', 'bird', 'cat', 'dog', 'horse',
                  'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe'
                  ]

    indoor_classes = ['__background__', 'bicycle', 'car', 'motorcycle',
                      'boat', 'bench', 'backpack',
                      'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
                      'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                      'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
                      'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
                      'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
                      'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
                      'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
                      'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
                      'scissors', 'teddy bear', 'hair drier', 'toothbrush']

    cat2ind = {}
    ind2cat = {}
    for i, class_ in enumerate(classes):
        if class_ not in not_indoor:
            cat2ind[class_] = i
            ind2cat[i] = class_

    cat2ind_indoor = {}
    for i, class_ in enumerate(indoor_classes):
        cat2ind_indoor[class_] = i

    return cat2ind, ind2cat, cat2ind_indoor


def load_palette(palette_path):
    ''' Load pre-made color palettes.
    '''
    with open(palette_path, 'r') as f:
        temp = f.readlines()
    colors = np.zeros((len(temp), 3), dtype=int)
    for ind, line in enumerate(temp):
        colors[ind, :] = np.asarray(line[:-1].split(",")).astype(int)
    return colors
