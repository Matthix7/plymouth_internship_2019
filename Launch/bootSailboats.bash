#!/bin/bash

echo "`date +%s`" > /home/sailboats/sailboats.txt
sleep 30
source /opt/ros/melodic/setup.bash
source /home/sailboats/workspaceRos/devel/setup.bash
echo "`date +%s`" >> /home/sailboats/sailboats.txt
roslaunch plymouth_internship_2019 sailboatBoot.launch
