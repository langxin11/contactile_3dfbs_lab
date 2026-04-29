cmake_minimum_required(VERSION 3.10)
project(minimal_reader CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 引用项目内原厂 C++ SDK（symlink -> ../../../vendor/C++LIN）
set(CONTACTILE_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/contactile_ptsdk")

include_directories(${CONTACTILE_SDK_DIR})
link_directories(${CONTACTILE_SDK_DIR})

add_executable(minimal_reader minimal_reader.cpp)
target_link_libraries(minimal_reader libPTSDK.a pthread)
