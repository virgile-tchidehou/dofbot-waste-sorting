cmake_minimum_required(VERSION 3.0.2)
project(dofbot_tri)

find_package(catkin REQUIRED COMPONENTS
  std_msgs
  rospy
  roscpp
  sensor_msgs
  image_transport
  cv_bridge
  message_generation
)

## Déclaration des services
add_service_files(
  FILES
  Classify.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
  sensor_msgs
)

catkin_package(
  CATKIN_DEPENDS 
    std_msgs 
    rospy 
    roscpp 
    sensor_msgs 
    image_transport 
    cv_bridge 
    message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

## Installation CORRECTE des scripts Python
catkin_install_python(PROGRAMS
  scripts/vision_node.py
  scripts/final_camera_node.py
  scripts/i2c_controller_node.py
  scripts/dofbot_tri_system.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
