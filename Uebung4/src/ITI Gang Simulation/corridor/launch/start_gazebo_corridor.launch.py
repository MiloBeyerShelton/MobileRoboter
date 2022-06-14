#!/usr/bin/env python3
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

import os
import sys

import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    """Starts a gazebo simulation and load the ITI corridor world."""

    for arg in sys.argv:
        if arg.startswith("gazebo_world:="):  # Name of the gazebo world
            world_name = arg.split(":=")[1]
        elif arg.startswith("robot:="):  # The type of robot
            robot = arg.split(":=")[1]
        else:
            if arg not in ['/opt/ros/foxy/bin/ros2',
                           'launch',
                           'corridor',
                           'start_gazebo_corridor.launch.py']:
                print("Argument not known: '", arg, "'")

    world_directory = os.path.join(get_package_share_directory('corridor'), 'worlds')

    ld = LaunchDescription()

    ld.add_action(ExecuteProcess(
        cmd=['gazebo', [world_directory, '/', world_name], '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    ))

    ld.add_action(launch_ros.actions.Node(
        package='corridor',
        executable='add_bot_node',
        output='screen',
        arguments=[
            '-x', '0.0',
            '-y', ['0.0'],
            '-z', '0.1',
            '--type_of_robot', robot
        ]
    ))
    return ld
