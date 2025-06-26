# Vision Enabled Miniature Robot

In Terminal Run,

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:<ROS_WORKSPACE>/src/miniature-robot-gazebo-simulation/miniature_robot_description/models
```

Make sure to replace, <ROS_WORKSPACE> with your actual ROS Workspace in above command, for example,

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/user/catkin_ws/src/miniature-robot-gazebo-simulation/miniature_robot_description/models
```

Or run this command from Inside your ROS Workspace Directory to export Gazebo Model Path

```
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$PWD/src/miniature-robot-gazebo-simulation/miniature_robot_description/models
```

### Running the Simulation

To run the simulation in Gazebo environment, first source the workspace using following command, inside your ROS Workspace

```bash
source devel/setup.bash
```

then run the Launch file from terminal using command,

```
roslaunch miniature_robot_description simulation.launch
```

#### Visualization of Robot Sensors

The robot is equipped with LiDAR and RGB Camera sensors. We can visualize the data gathered by sensors using ROS Topics in Terminal or RViz.

To visualize camera feed run,

```bash
rosrun image_view image_view image:=/miniature_robot/camera/image_raw
```

To visualize LiDAR data, run the following command

```
rostopic echo /miniature_robot/laser/scan
```

