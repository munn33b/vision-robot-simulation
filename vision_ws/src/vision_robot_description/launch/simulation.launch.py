import os
import launch
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch_ros.parameter_descriptions import ParameterValue
import xacro
from launch.event_handlers import OnProcessExit
from launch.actions import RegisterEventHandler


def generate_launch_description():

    ros_gz_bridge_config_file_path = 'config/ros_gz_bridge.yaml'

    package_name_gazebo = 'vision_robot_description'
    pkg_share_gazebo = FindPackageShare(package=package_name_gazebo).find(package_name_gazebo)
    default_robot_name = 'VBot_v1'
    pkg_name = FindPackageShare(package="vision_robot_description").find("vision_robot_description")

    robot_name = LaunchConfiguration('robot_name')

    default_ros_gz_bridge_config_file_path = os.path.join(pkg_name, ros_gz_bridge_config_file_path)

    # Declare the launch argument first
    declare_robot_name_cmd = DeclareLaunchArgument(
      name='robot_name',
      default_value=default_robot_name,
      description='The name for the robot')


    urdf_file_path = 'urdf/vision_robot.urdf.xacro'
    default_urdf_model_path = os.path.join(pkg_share_gazebo, urdf_file_path)

    doc = xacro.parse(open(default_urdf_model_path))
    xacro.process_doc(doc)

    bras_robot_description_path = FindPackageShare("vision_robot_description").find("vision_robot_description")

    # Define the models directory inside the package
    models_path = os.path.join(bras_robot_description_path, "models")
    workspace_src_path = os.path.abspath(os.path.join(bras_robot_description_path, "../../../vision_robot_description/share"))


    os.environ["IGN_GAZEBO_RESOURCE_PATH"] = f"{models_path}:{workspace_src_path}"
    print (os.environ["IGN_GAZEBO_RESOURCE_PATH"])


    world_file = os.path.join(
        get_package_share_directory('vision_robot_description'),
        'worlds',
        'simulation_world_new.sdf'
    )

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare('vision_robot_description'),
            'config',
            'vision_robot_controllers.yaml',
        ]
    )


    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
          'config_file': default_ros_gz_bridge_config_file_path,
        }],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name="camera_node",
        arguments=['/camera@sensor_msgs/msg/Image@ignition.msgs.Image'],
    )

    ign_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_ign_gazebo'),
            'launch',
            'ign_gazebo.launch.py'
        )]),
        launch_arguments={
                'ign_args': f' -r -v 4 {world_file} '
        }.items()
    )




    start_gazebo_ros_spawner_cmd = Node(
      package='ros_gz_sim',
      executable='create',
      arguments=[
        '-string', doc.toxml(),
        '-name', robot_name,
        '-allow_renaming', 'true',
        '-x', '0.663025',
        '-y', '-0.449473',
        '-z', '0.045598',
        '-R', '0',
        '-P', '0',
        '-Y', '-3.14',
        ],
      output='screen')

    robot_description_content = doc.toxml()

    robot_description = {'robot_description': robot_description_content}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )



    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        name="ros2_control_node_custom",
        parameters=[robot_description, robot_controllers],
        output={
            "stderr": "screen",
        },
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        parameters=[{'use_sim_time': False}],
        arguments=['joint_state_broadcaster'],
    )

    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_controller',
            '--param-file',
            robot_controllers,
            ],
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            'gripper_controller',
            '--param-file',
            robot_controllers,
            ]
        )




  # Launch the arm controller after launching the joint state broadcaster




    return launch.LaunchDescription([
        declare_robot_name_cmd,  # Ensure this is declared first
        ign_gazebo,
        bridge,
        start_gazebo_ros_bridge_cmd,
        joint_state_broadcaster_spawner,
        start_gazebo_ros_spawner_cmd,
        joint_trajectory_controller_spawner,
        #gripper_controller_spawner,
        #control_node,
        node_robot_state_publisher
    ])

