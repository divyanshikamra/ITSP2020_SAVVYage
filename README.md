# ITSP2020_SAVVYage

This repo contains all the files built underthe software subsystem of Team SAVVYage under ITSP 2020.
(These files have been made and tested on ROS melodic)

## To see the working of these files:
1. You need to have ROS, Gazebo and RviZ installed.
2. Clone this repository into your rosworkspace.
3. run **catkin_make** command inside this workspace via terminal
4. now run **source devel/setup.bash** command inside this workspace via terminal
5. To launch the bot and environment, run command:
'''roslaunch savvyage_gazebo savvyage.launch'''
6. To start live mapping using RviZ:
'''roslaunch motion_plan gmapping.launch'''
7. To start the path planning algorithm, run command:
'''roslaunch motion_plan learn.launch target:=conference'''
(this command will send the bot to conference room, you can enter any location from the following: room-1, room-2, room-3, washroom-1, washroom-2, gate, store, lounge)
With this the bot will plan it's own path and go from one place to another.

