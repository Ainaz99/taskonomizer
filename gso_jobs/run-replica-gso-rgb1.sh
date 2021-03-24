#!/usr/bin/env bash
# Passed arguments : --scene_path  with  {args}*

#ae-habitat

buildings=(frl_apartment_0 frl_apartment_1 frl_apartment_2 frl_apartment_3 frl_apartment_4 frl_apartment_5)

densities=(3 6 15)

path=/scratch-data/ainaz/replica-google-objects

for building in "${buildings[@]}"; do
  for i in "${densities[@]}"; do
    ./taskonomizer.sh --model_path=$path/$building/$i/ --task=rgb_objs
    echo $building' - '$i' rgb done!' >> $building.txt
  done
done