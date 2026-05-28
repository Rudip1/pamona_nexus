cmake_minimum_required(VERSION 3.8)
project(pomona_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Day 1: no interfaces. When you add a .msg, list it here:
#
#   set(MSG_FILES
#     msg/Example.msg
#   )
#
#   rosidl_generate_interfaces(${PROJECT_NAME}
#     ${MSG_FILES}
#     DEPENDENCIES std_msgs geometry_msgs sensor_msgs
#   )
#
#   ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
