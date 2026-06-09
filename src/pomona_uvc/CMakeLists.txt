cmake_minimum_required(VERSION 3.8)
project(pomona_uvc)

find_package(ament_cmake REQUIRED)

# ── Python control node (lamp on/off services + disinfection dose map) ───────
install(PROGRAMS scripts/uvc_controller.py
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch rviz
  DESTINATION share/${PROJECT_NAME})

ament_package()
