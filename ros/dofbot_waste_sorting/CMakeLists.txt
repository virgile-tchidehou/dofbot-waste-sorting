cmake_minimum_required(VERSION 3.0.2)
project(dofbot_waste_sorting)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
  message_generation
)

add_service_files(
  FILES
  Classify.srv
)

generate_messages(
  DEPENDENCIES
  sensor_msgs
)

catkin_package(
  CATKIN_DEPENDS
    rospy
    std_msgs
    sensor_msgs
    cv_bridge
    message_runtime
)

catkin_install_python(PROGRAMS
  scripts/camera_node.py
  scripts/vision_node.py
  scripts/sorting_controller_node.py
  scripts/sorting_sequence_demo.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY
  launch
  config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
