# Snowball Demo!


## Installation
We provide a docker that contains all the necessary libraries. It's simple to install and run.

 1. Clone the repo:
```bash
git clone ...
cd Snowball
```

 2. Simply run:
```bash
./install.sh
```

Now the installation is complete, and all the necessary libraries are installed in the docker.

## Run Demo
| Surface Normals | Euclidean Depth | Semantics  |
| :-------------: |:-------------:| :-----:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/normal/point_0002_view_equirectangular_domain_normal.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/depth_euclidean/point_0002_view_equirectangular_domain_depth_euclidean.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/semantic/point_0002_view_equirectangular_domain_semantic.png) |
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/normal/point_0009_view_equirectangular_domain_normal.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/depth_euclidean/point_0009_view_equirectangular_domain_depth_euclidean.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/semantic/point_0009_view_equirectangular_domain_semantic.png) |
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/normal/point_0010_view_equirectangular_domain_normal.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/depth_euclidean/point_0010_view_equirectangular_domain_depth_euclidean.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/pano/semantic/point_0010_view_equirectangular_domain_semantic.png)


Next, we show how to generate data for different tasks. You can see the list of tasks below:

```bash
RGB (8-bit)              Surface-Normals (8-bit)     Curvature (8-bit)
Reshading (8-bit)        Depth ZBuffer (16-bit)      Depth Euclidean (16-bit)
Edge 2D (16-bit)         Edge 3D (16-bit)            Keypoints 2D (16-bit)
Keypoints 3D (16-bit)    Segmentation 2D (8-bit)     Segmentation 2.5D (8-bit)
Semantic Segmentation (8-bit)
```



**To run the Snowball for a specific task:**
``` bash

./Snowball.sh --model_path=$PATH_TO_FOLDER_OF_MODEL --task=$TASK \
      with {SETTING=VALUE}*

```

The `--model_path` tag specifies the path to the folder containing the mesh, where the data from all other tasks will also be saved. The `--task` tag specifies the target task for generating the data. You can generate all the tasks using `--task=all` .
You can also specify different setting values for each task in the command. The list of all settings defined for different tasks are in `settings.py`.

The final folder structure will be as follows:
```bash
model_path
│   mesh.ply
│   mesh_semantic.ply
│   texture.png
│   camera_poses.json   
└─── point_info
└─── rgb
└─── normals
└─── depth_zbuffer
│   ...
│   
└─── pano
│   └─── point_info
│   └─── rgb
│   └─── normal
│   └─── depth_euclidean
```

Now, we run the Snowball for different tasks.

### 1. Generating points:
In order to generate the points, we need camera poses. You can either generate new camera poses or read them from a `json` file.

#### Read camera poses from json file:
The following command generates 100 points using the camera poses defined in `camera_poses.json`.
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=points \
   with GENERATE_CAMERAS=False CAMERA_POSE_FILE=camera_poses.json \
        MIN_VIEWS_PER_POINT=3  NUM_POINTS=100 \
        MODEL_FILE=mesh.ply    POINT_TYPE=CORRESPONDENCES
```
In order to read the camera poses from the json file, you should specify `GENERATE_CAMERAS=False`. This json file should contain `location` and `quaternion rotation (wxyz)` for a list of cameras.
Below, you can see how this information should be saved for each camera.

```javascript
{
    "camera_id": "0000",
    "location": [0.2146, 1.2829, 0.2003],
    "rotation_quaternion": [0.0144, -0.0100, -0.0001,-0.9998]
}
```
You can specify the type of generated points. `POINT_TYPE=CORRESPONDENCES` is used for generating fixated images. Switch to `POINT_TYPE=SWEEP` in case you want to generate panoramas.
#### Generate new camera poses:
You can generate new camera poses before generating the points using `GENERATE_CAMERAS=True`.
There are 2 ways for generating the camera poses depending on wether the mesh is a building (like in Replica) or is an object (Google Scanned Objects).

##### Generate camera poses inside a building:
In this case, you have to specify `BUILDING=True`.

```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=points \
   with GENERATE_CAMERAS=True     BUILDING=True \
        MIN_CAMERA_HEIGHT=1       MAX_CAMERA_ROLL=10 \
        MIN_CAMERA_DISTANCE=1   MIN_CAMERA_DISTANCE_TO_MESH=0.3 \
        MIN_VIEWS_PER_POINT=3     POINTS_PER_CAMERA=5 \
        MODEL_FILE=mesh.ply       POINT_TYPE=CORRESPONDENCES

```
Camera locations are sampled inside the mesh using **Poisson Disc Sampling** to cover the whole space. Minimum distance between cameras is specified by `MIN_CAMERA_DISTANCE`. `MIN_CAMERA_DISTANCE_TO_MESH` also defines the minimum distance of each camera to the closest point of the mesh.
Camera `yaw` is sampled uniformly in `[-180°, 180°]`, camera `roll` comes from a truncated normal distribution in `[-MAX_CAMERA_ROLL, MAX_CAMERA_ROLL]`, and camera `pitch` will be specified in the point generation process.
More camera settings such as  `MIN_CAMERA_HEIGHT`,  `MAX_CAMERA_HEIGHT`, etc. are defined in `settings.py`.
You can specify the number of generated points either by `NUM_POINTS` or `NUM_POINTS_PER_CAMERA`. In case we have `NUM_POINTS=None`, the number of generated points will be `NUM_POINTS_PER_CAMERA * number of cameras`.

##### Generate camera poses for an object:
If the mesh is an object you have to specify `BUILDING=False`. In this case, camera locations will be sampled on a `sphere` surrounding the mesh. You can specify the number of generated cameras by `NUM_CAMERAS`. Camera rotations will be sampled the same as above.

```bash
./Snowball.sh --model_path=google_scanned_objects/TEA_SET --task=points \
  with GENERATE_CAMERAS=True    BUILDING=False \
       NUM_CAMERAS=12           MAX_CAMERA_ROLL=10 \
       POINTS_PER_CAMERA=5      MIN_VIEWS_PER_POINT=3 \
       MODEL_FILE=model.obj     POINT_TYPE=CORRESPONDENCES
```

### 2. Surface Normals:

In order to generate surface normal images simply run:
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=normal \
    with MODEL_FILE=mesh.ply  CREATE_FIXATED=True
```
This will generate fixated photos.

| RGB | Surface Normals (Snowball) | Surface Normals (Consistency model) |
| :-------------: |:-------------:| :-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_246_view_34_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/normal/point_246_view_34_domain_normal.png) | ![](/home/ainaz/Desktop/replica/selected_replica/point_246_view_34.png)
| ![](/home/ainaz/Desktop/clevr/rgb/point_55_view_0_domain_rgb.png)  | ![](/home/ainaz/Desktop/clevr/rgb/point_55_view_0_domain_normal.png)  |  ![](/home/ainaz/Desktop/clevr/rgb/point_55/point_55_view_0_domain_rgb_normal_consistency.v1.png) |
| ![](/home/ainaz/Desktop/google_scanned/Vtech_Roll_Learn_Turtle/selected_turtle/point_28_view_1_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/Vtech_Roll_Learn_Turtle/selected_turtle/point_28_view_1_domain_normal.png) | ![](/home/ainaz/Desktop/google_scanned/Vtech_Roll_Learn_Turtle/selected_turtle/point_28_view_1/point_28_view_1_domain_rgb_normal_consistency.v1.png)
| ![](/home/ainaz/Desktop/google_scanned/Threshold_Porcelain_Teapot_White/selected_teapot/point_45_view_1_domain_rgb.png) |  ![](/home/ainaz/Desktop/google_scanned/Threshold_Porcelain_Teapot_White/selected_teapot/point_45_view_1_domain_normal.png) | ![](/home/ainaz/Desktop/google_scanned/Threshold_Porcelain_Teapot_White/selected_teapot/point_45_view_1/point_45_view_1_domain_rgb_normal_consistency.v1.png)
| ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) |  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_normal.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5/point_21_view_5_domain_rgb_normal_consistency.v1.png)

In case you want to generate panoramas switch to `CREATE_FIXATED=False`  and `CREATE_PANOS=True`:
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=normal \
    with MODEL_FILE=mesh.ply CREATE_FIXATED=False CREATE_PANOS=True
```
![](/home/ainaz/Desktop/EPFL/replica_apartment_0/pano/normal/point_0019_view_equirectangular_domain_normal.png)

### 3. Depth ZBuffer:
To generate depth zbuffer images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=depth_zbuffer \
    with MODEL_FILE=mesh.ply  DEPTH_ZBUFFER_MAX_DISTANCE_METERS=16
```
ZBuffer depth is defined as the distance to the camera plane.
You can specify the depth sensitivity by `DEPTH_ZBUFFER_MAX_DISTANCE_METERS`. With 16m and and 16-bit images, we will have depth sensitivity equal to 16 / 2**16 = 1/4096 meters.

| RGB | Zbuffer Depth (Snowball)| Zbuffer Depth (Consistency model)|
| :-------------: |:-------------:| :-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_156_view_10_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/depth_zbuffer/point_156_view_10_domain_depth_zbuffer.png) | ![](/home/ainaz/Desktop/replica/selected_replica/point_156_view_10/point_156_view_10_domain_rgb_depth_consistency.v1.png)
|  ![](/home/ainaz/Desktop/Paper2/figures/fig1_data_modalities/clevr/point_2368_view_0_domain_rgb.png) | ![](/home/ainaz/Desktop/Paper2/figures/fig1_data_modalities/clevr/point_2368_view_0_domain_depth_zbuffer.png)  |  ![](/home/ainaz/Desktop/clevr/rgb/point_100/point_100_view_0_domain_rgb_depth_consistency.v1.png) |
| ![](/home/ainaz/Desktop/google_scanned/BEDROOM_CLASSIC/selected_bedroom/point_24_view_3_domain_rgb.png)  | ![](/home/ainaz/Desktop/google_scanned/BEDROOM_CLASSIC/selected_bedroom/point_24_view_3_domain_depth_zbuffer.png)  | ![](/home/ainaz/Desktop/google_scanned/BEDROOM_CLASSIC/selected_bedroom/point_24_view_3/point_24_view_3_domain_rgb_depth_consistency.v1.png)  |
|  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_depth_zbuffer.png)  | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5/point_21_view_5_domain_rgb_depth_consistency.v1.png)  |

### 4. Depth Euclidean:
To generate depth euclidean images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=depth_euclidean \
    with MODEL_FILE=mesh.ply  DEPTH_EUCLIDEAN_MAX_DISTANCE_METERS=16
```
Euclidean depth is measured as the distance from each pixel to the camera’s optical center. You can specify depth sensitivity the same as above.

### 5. Reshading:
To generate reshading images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=reshading \
    with MODEL_FILE=mesh.ply  LAMP_ENERGY=2.5
```

| RGB | Reshading (Snowball)| Reshading (Consistency model)|
| :-------------: |:-------------:| :-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_87_view_13_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/reshading/point_87_view_13_domain_reshading.png) | ![](/home/ainaz/Desktop/replica/selected_replica/point_87_view_13/point_87_view_13_domain_rgb_reshading_consistency.v3.png)
|  ![](/home/ainaz/Desktop/clevr/rgb/point_50_view_0_domain_rgb.png) | ![](/home/ainaz/Desktop/clevr/rgb/point_50_view_0_domain_reshading.png)  | ![](/home/ainaz/Desktop/clevr/rgb/point_50/point_50_view_0_domain_rgb_reshading_consistency.v1.png)  |
| ![](/home/ainaz/Desktop/google_scanned/Vtech_Stack_Sing_Rings_636_Months/selected_monkey/point_5_view_2_domain_rgb_new.png)  | ![](/home/ainaz/Desktop/google_scanned/Vtech_Stack_Sing_Rings_636_Months/selected_monkey/point_5_view_2_domain_reshading.png)  | ![](/home/ainaz/Desktop/google_scanned/Vtech_Stack_Sing_Rings_636_Months/selected_monkey/point_5_view_2/point_5_view_2_domain_rgb_new_reshading_consistency.v1.png)  |
|  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_reshading.png)  | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5/point_21_view_5_domain_rgb_reshading_consistency.v1.png)  

### 6. Principal Curvature:
To generate principal curvature images run:

```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=curvature with MIN_CURVATURE_RADIUS=0.03
```

| RGB | 3D keypoints |
| :-------------: |:-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_0_view_2_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_0_view_2_domain_principal_curvature.png)
|  ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_0_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_0_view_5_domain_principal_curvature.png)

### 7. Keypoints 2D:
2D keypoints are generated from corresponding `rgb` images for each point and view. You can generate 2D keypoint images using the command below :

```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=keypoints2d
```

### 8. Keypoints 3D:
3D keypoints are similar to 2D keypoints except that they are derived from 3D data. Therefore you have to generate `depth_zbuffer` images for each point before generating 3D keypoints.
To generate 3D keypoint images use the command below:
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=keypoints3d \
    with KEYPOINT_SUPPORT_SIZE=0.3
```
`KEYPOINT_SUPPORT_SIZE` specifies the diameter of the sphere around each 3D point that is used to decide if the point should be a point of interest. 0.3 meters is suggested for indoor spaces.

| RGB | 3D keypoints |
| :-------------: |:-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_7_view_15_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/keypoints3d/point_7_view_15_domain_keypoints3d.png)
|  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_keypoints3d.png)


### 9. Edge 2D:
2D Edge images are computed from corresponding `rgb` images using **Canny edge detection** algorithm.
To generate 2D edge images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=edge2d \
    with CANNY_RGB_BLUR_SIGMA=3.0
```
`CANNY_RGB_BLUR_SIGMA` specifies the sigma in Gaussian filter used in Canny edge detector.

| RGB | 2D Edge |
| :-------------: |:-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_202_view_22_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/edge_texture/point_202_view_22_domain_edge_texture.png)
|  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_edge_texture.png)


### 10. Edge 3D:
3D Edge images are derived from `depth_zbuffer` images, so you have to generate those first. To generate 3D edge images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=edge3d
  with EDGE_3D_THRESH=None
```

### 11. Segmentation 2D:
2D Segmentation images are generated using **Normalized Cut** algorithm from corresponding `rgb` images. To generate 2D segmentation images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=segment2d \
  with SEGMENTATION_2D_BLUR=3     SEGMENTATION_2D_CUT_THRESH=0.005  \
       SEGMENTATION_2D_SCALE=200  SEGMENTATION_2D_SELF_EDGE_WEIGHT=2
```


### 11. Segmentation 2.5D:
Segmentation 2.5D uses the same algorithm as 2D, but the labels are computed jointly from the `edge3d` image, `depth_zbuffer` image, and `surface normals`image. 2.5D segmentation incorporates information about the scene geometry that is not directly present in the `rgb` image. To generate 2.5D segmentation images :
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=segment25d \
  with SEGMENTATION_2D_SCALE=200        SEGMENTATION_25D_CUT_THRESH=1  \
       SEGMENTATION_25D_DEPTH_WEIGHT=2  SEGMENTATION_25D_NORMAL_WEIGHT=1 \
       SEGMENTATION_25D_EDGE_WEIGHT=10
```
You can specify the weights for each of the `3D edge`, `depth_zbuffer`, and `surface normals` images used in 2.5D segmentation algorithm by `SEGMENTATION_25D_EDGE_WEIGHT`, `SEGMENTATION_25D_DEPTH_WEIGHT`, and `SEGMENTATION_25D_NORMAL_WEIGHT` respectively.

| RGB | 2.5D Segmentation |
| :-------: |:-------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_300_view_0_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/segment_unsup25d/point_300_view_0_domain_segment_unsup25d.png)
|  ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/TEA_SET/selected_teaset/point_21_view_5_domain_segment_unsup25d.png)

### 12. Semantic Segmentation:
In order to generate semantic photos, we need to have mesh face colors. These colors should be saved as a face property named `color` in the `.ply` file.

Below, you can see how this `color` property should be saved in `mesh_semantic.ply`.

```bash
>>> from plyfile import PlyData
>>> model = PlyData.read('mesh_semantic.ply')
>>> faces = model.elements[1]
>>> faces.properties
(PlyListProperty('vertex_indices', 'uchar', 'int'), PlyListProperty('color', 'uchar', 'int'))
>>> faces['color']
array([array([ 96, 118,  19], dtype=int32),
       array([ 48, 110, 165], dtype=int32),
       array([ 96, 118,  19], dtype=int32), ...,
       array([10, 10, 10], dtype=int32), array([10, 10, 10], dtype=int32),
       array([10, 10, 10], dtype=int32)], dtype=object)
>>>
```
To generate semantic segmentation photos, run the command below:
```bash
./Snowball.sh --model_path=/usr/Snowball/frl_apartment_0 --task=semantic \
  with SEMANTIC_MODEL_FILE=mesh_semantic.ply
```
Notice that you should specify the value for `SEMANTIC_MODEL_FILE` instead of `MODEL_FILE` which was used for other tasks.

| RGB | Semantic Segmentation |
| :-------------: |:-------------:|
| ![](/home/ainaz/Desktop/replica/replica_apartment_0/rgb/point_84_view_6_domain_rgb.png)  | ![](/home/ainaz/Desktop/replica/replica_apartment_0/semantic/point_84_view_6_domain_semantic.png)
|![](/home/ainaz/Desktop/clevr/complex/point_3_view_0_domain_rgb.png)   |  ![](/home/ainaz/Desktop/clevr/complex/point_3_view_0_domain_semantic.png) |


### 13. RGB:
There are several ways to generate rgb images.
#### Generate rgb images using texture UV map:
You can generate `rgb` images for each point and view using texture UV map. You should specify the texture file using `TEXTURE_FILE`.
```bash
./Snowball.sh --model_path=google_scanned_objects/Vtech_Stack_Sing_Rings_636_Months --task=rgb \
    with MODEL_FILE=mesh.ply  CREATE_FIXATED=True \
         USE_TEXTURE=True     TEXTURE_FILE=texture.png
```
|  |  |  |  |
| :-------: |:-------:| :-------:| :-------:|
|  ![](/home/ainaz/Desktop/google_scanned/RJ_Rabbit_Easter_Basket_Blue/selected_basket/point_22_view_0_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/RJ_Rabbit_Easter_Basket_Blue/selected_basket/point_19_view_4_domain_rgb.png) |  ![](/home/ainaz/Desktop/google_scanned/RJ_Rabbit_Easter_Basket_Blue/selected_basket/point_21_view_0_domain_rgb.png) | ![](/home/ainaz/Desktop/google_scanned/RJ_Rabbit_Easter_Basket_Blue/selected_basket/point_22_view_0_domain_rgb.png)
