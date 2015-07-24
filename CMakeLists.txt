cmake_minimum_required(VERSION 2.8.3)

project(respec)

find_package(catkin REQUIRED COMPONENTS)

## Uncomment this if the package has a setup.py. This macro ensures
## modules and global scripts declared therein get installed
## See http://ros.org/doc/api/catkin/html/user_guide/setup_dot_py.html
catkin_python_setup()

# specify catkin-specific information
catkin_package()
