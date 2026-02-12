cmake_minimum_required(VERSION 3.16)

# --- vcpkg toolchain auto-detect (must be BEFORE project()) ---
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    if(DEFINED ENV{VCPKG_ROOT})
        set(_VCPKG_TOOLCHAIN "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
        if(EXISTS "${_VCPKG_TOOLCHAIN}")
            set(CMAKE_TOOLCHAIN_FILE "${_VCPKG_TOOLCHAIN}" CACHE FILEPATH "vcpkg toolchain" FORCE)
        endif()
    endif()
endif()

# If something set a broken toolchain like "/scripts/buildsystems/vcpkg.cmake", fix it
if(DEFINED CMAKE_TOOLCHAIN_FILE AND CMAKE_TOOLCHAIN_FILE MATCHES "^/scripts/buildsystems/vcpkg.cmake$")
    if(DEFINED ENV{VCPKG_ROOT})
        set(_VCPKG_TOOLCHAIN "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
        if(EXISTS "${_VCPKG_TOOLCHAIN}")
            set(CMAKE_TOOLCHAIN_FILE "${_VCPKG_TOOLCHAIN}" CACHE FILEPATH "vcpkg toolchain" FORCE)
        endif()
    endif()
endif()

project(mini_arcade_native_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Let vcpkg toolchain be used if user sets CMAKE_TOOLCHAIN_FILE env var.
# (scikit-build-core will pass env vars to CMake.)

find_package(pybind11 CONFIG REQUIRED)
find_package(SDL2 CONFIG REQUIRED)
find_package(SDL2_ttf CONFIG REQUIRED)
find_package(SDL2_mixer CONFIG REQUIRED) 

set(TARGET_NAME _native)

set(NATIVE_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/src/native)
set(NATIVE_INC  ${NATIVE_ROOT}/include)

set(NATIVE_SOURCES
    ${NATIVE_ROOT}/bindings.cpp
    ${NATIVE_ROOT}/backend.cpp
    ${NATIVE_ROOT}/platform.cpp
    ${NATIVE_ROOT}/window.cpp
    ${NATIVE_ROOT}/input.cpp
    ${NATIVE_ROOT}/capture.cpp
    ${NATIVE_ROOT}/audio.cpp
    ${NATIVE_ROOT}/sdl_renderer.cpp
    ${NATIVE_ROOT}/sdl_text.cpp
    ${NATIVE_ROOT}/capture_bytes.cpp
)

pybind11_add_module(${TARGET_NAME} ${NATIVE_SOURCES})

target_include_directories(${TARGET_NAME}
    PRIVATE
        ${NATIVE_INC}
)

# # C++ sources live under cpp/
# pybind11_add_module(${TARGET_NAME}
#     cpp/bindings.cpp
#     cpp/engine.cpp
# )

target_link_libraries(${TARGET_NAME} PRIVATE SDL2::SDL2 SDL2_ttf::SDL2_ttf SDL2_mixer::SDL2_mixer)

# Install the compiled extension into the Python package directory
# so it ends up as mini_arcade_native_backend/_native.*.pyd
install(TARGETS ${TARGET_NAME}
        LIBRARY DESTINATION mini_arcade_native_backend
        RUNTIME DESTINATION mini_arcade_native_backend
        ARCHIVE DESTINATION mini_arcade_native_backend)
