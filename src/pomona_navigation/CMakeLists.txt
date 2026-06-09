cmake_minimum_required(VERSION 3.8)
project(pomona_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Python module (compose_params + bed_waypoints) — importable by launch files.
ament_python_install_package(${PROJECT_NAME})

# Config, launchers, behavior trees, rviz.
install(
  DIRECTORY config behavior_trees launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Mission node — runnable via `ros2 run` / launch Node(executable=...).
install(
  PROGRAMS nodes/bed_disinfection_mission.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
