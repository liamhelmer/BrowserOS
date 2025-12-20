cmake_minimum_required(VERSION 3.22.1)

project("mcp_server")

# Add the native library
add_library(
    mcp_server
    SHARED
    mcp_server/mcp_server_jni.cpp
)

# Find required libraries
find_library(log-lib log)

# Link libraries
target_link_libraries(
    mcp_server
    ${log-lib}
)
