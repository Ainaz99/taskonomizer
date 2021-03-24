#!/usr/bin/env bash


# Passed arguments : --scene_path  with  {args}*

# while [[ "$#" -gt 0 ]]; do
#     case $1 in
#         --building=*) 
#           building="${1#*=}"
#           ;; 
#         with) 
#         break
#         ;;
#         *) echo "Unknown parameter passed: $1"; exit 1 ;;
#     esac
#     shift
# done

densities=(3 6 15)
tasks=(semantic_objs)

for path in /scratch-data/ainaz/replica-google-objects/*
do

  for task in "${tasks[@]}"; do
    for i in "${densities[@]}"; do
      ./taskonomizer.sh --model_path=$path/$i/ --task=$task with MODEL_FILE=mesh_semantic.ply
      echo $path' - '$i' - '$task' done!' >> semantic.txt
    done
  done
done

