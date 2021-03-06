#!/usr/bin/env bash

# Passed arguments : task  model_path  {args}*

task=$1
model_path=$2

args="${@:3}"


case $task in
  normal)
    bash jobs/create_normal_images_job.sh $model_path $args
    ;;
  depth_zbuffer)
    bash jobs/create_depth_zbuffer_images_job.sh $model_path $args
    ;;
  depth_euclidean)
    bash jobs/create_depth_euclidean_images_job.sh $model_path $args
    ;;
  rgb)
    bash jobs/create_rgb_images_replica_job.sh $model_path $args
    ;;
  reshading)
    bash jobs/create_reshade_images_job.sh $model_path $args
    ;;
  edge3d)
    bash jobs/create_edge3d_images_job.sh $model_path $args
    ;;
  edge2d)
    bash jobs/create_edge2d_images_job.sh $model_path $args
    ;;
  keypoints3d)
    bash jobs/create_keypoints_3d_images_job.sh $model_path $args
    ;;
  keypoints2d)
    bash jobs/create_keypoints_2d_images_job.sh $model_path $args
    ;;
  segment2d)
    bash jobs/create_segment2d_images_job.sh $model_path $args
    ;;
  segment25d)
    bash jobs/create_segment25d_images_job.sh $model_path $args
    ;;
  semantic)
    bash jobs/create_semantic_images_replica_job.sh $model_path $args
    ;;
  vanishing_points)
    bash jobs/create_vanishing_points_job.sh $model_path $args
    ;;
  curvature_mesh)
    bash jobs/create_curvature_meshes_job.sh $model_path $args
    ;;
  curvature)
    bash jobs/create_curvature_images_job.sh $model_path $args
    ;;
  points)
    bash jobs/generate_points_job.sh $model_path $args
    ;;
  mask_valid)
    bash jobs/create_mask_valid_job.sh $model_path $args
    ;;
  rgb_trajectory)
    bash jobs/create_rgb_images_trajectory_job.sh $model_path $args
    ;;
  simulate)
    bash jobs/simulate_replica_google_objects_job.sh $model_path $args
    ;;
  points_objs)
    bash jobs/generate_points_obj_view_job.sh $model_path $args
    ;;
  rgb_objs)
    bash jobs/create_rgb_images_replica_google_objects_job.sh $model_path $args
    ;;
  semantic_objs)
    bash jobs/create_semantic_images_replica_google_objects_job.sh $model_path $args
    ;;
  add_objs)
    bash jobs/add_google_objects_job.sh $model_path $args
    ;;
  join)
    bash jobs/join_meshes_blendedMVS.sh $model_path $args
    ;;
  *)
    echo "ERROR : TASK NOT DEFINED!"
    exit 125
esac
