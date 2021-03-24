#!/usr/bin/env bash


# Passed arguments : --scene_path  with  {args}*

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --building=*) 
          building="${1#*=}"
          ;; 
        with) 
        break
        ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done



path=/scratch-data/ainaz/replica-google-objects/$building

densities=(15)
tasks=(normal depth_zbuffer mask_valid depth_euclidean edge2d edge3d keypoints2d keypoints3d segment2d segment25d)

for task in "${tasks[@]}"; do
  for i in "${densities[@]}"; do
    ./taskonomizer.sh --model_path=$path/$i/ --task=$task with MODEL_FILE=mesh_with_objs.ply
    echo $building' - '$i' - '$task' done!' >> $building.txt
  done
done

