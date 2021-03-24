#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Clear the directory if it exists
rm -rf rgb
rm -rf point_info
rm -rf trajectory.mkv
rm -rf video.mkv

# Make it if it doesn't
mkdir -p rgb
mkdir -p point_info


# Get additional arguments
args="${@:2}"

# Generate correspondences
python3 /scratch-data/ainaz/taskonomizer/scripts/create_rgb_images_trajectory.py -- \
MODEL_NAME=$1 MODEL_FILE=mesh.ply

python3 /scratch-data/ainaz/taskonomizer/scripts/create_trajectory_video.py -- \
MODEL_NAME=$1 MODEL_FILE=mesh.ply

mencoder -speed 22 -o trajectory.mkv -ovc lavc video.mkv
