cmake_minimum_required(VERSION 3.8)
project(pomona_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds models config rviz
  DESTINATION share/${PROJECT_NAME}
)

# Python nodes (run via ros2 run / launch Node executable=...)
install(
  PROGRAMS nodes/laser_self_filter.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
