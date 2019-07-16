cmake_minimum_required(VERSION 3.14)
project(rt_midi_test)

set(CMAKE_CXX_STANDARD 14)

include_directories ("${PROJECT_SOURCE_DIR}/rtmidi-tests")

add_executable(rt_midi_test main.cpp Probe.cpp Probe.h)

target_link_libraries (rt_midi_test rtmidi)