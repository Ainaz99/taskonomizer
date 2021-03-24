#!/usr/bin/env bash

buildings=('frl_apartment_0' 'frl_apartment_1' 'frl_apartment_2' 'frl_apartment_3' \
'frl_apartment_4' 'frl_apartment_5' 'apartment_0' 'apartment_1' 'apartment_2' \
'office_0' 'office_1' 'office_2' 'office_3' 'office_4' 'room_0' 'room_1' 'room_2')
path=/scratch-data/ainaz/replica-google-objects


for building in "${buildings[@]}"; do
    # ./progmesh $path/$building/habitat/mesh_semantic.ply $path/$building/mesh_decimated.ply 500000
    cp -r $path/hotel_0/mesh0.stage_config.json $path/$building/mesh.stage_config.json
done


