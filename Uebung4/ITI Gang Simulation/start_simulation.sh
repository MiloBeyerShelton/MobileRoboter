#!/bin/bash
#    Copyright 2022 Marian Begemann
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
colcon build --symlink-install --allow-overriding corridor
 source ./install/setup.bash &&
 tmp=":$(pwd)/build/corridor/models" &&
 GAZEBO_MODEL_PATH=$tmp&&
 echo $GAZEBO_MODEL_PATH&&
 ros2 launch corridor start_gazebo_corridor.launch.py \
 gazebo_world:=iti_gang_world.world \
 robot:=waffle_pi
# robot: burger | waffle_pi | jackal
