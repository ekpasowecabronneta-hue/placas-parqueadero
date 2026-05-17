cmake_minimum_required(VERSION 3.16)
project(placas_parqueadero LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(${CMAKE_SOURCE_DIR}/include)

# Core library (shared for SWIG + static for executables)
add_library(parking_core_obj OBJECT
    src/parking_core.cpp
    src/socket_platform.cpp
)

add_library(parking_core STATIC
    $<TARGET_OBJECTS:parking_core_obj>
)
target_include_directories(parking_core PUBLIC ${CMAKE_SOURCE_DIR}/include)

add_library(parking_core_shared SHARED
    src/parking_core.cpp
)
target_compile_definitions(parking_core_shared PRIVATE PARKING_CORE_EXPORTS)
target_include_directories(parking_core_shared PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Executables
add_executable(parking_server
    src/socket_server.cpp
    src/socket_platform.cpp
)
target_link_libraries(parking_server PRIVATE parking_core)

add_executable(parking_generator
    src/generator_main.cpp
    src/socket_platform.cpp
)
target_link_libraries(parking_generator PRIVATE parking_core)

if(WIN32)
    target_link_libraries(parking_server PRIVATE ws2_32)
    target_link_libraries(parking_generator PRIVATE ws2_32)
endif()

# SWIG Python module
find_package(SWIG QUIET)
find_package(Python3 COMPONENTS Interpreter Development QUIET)

if(SWIG_FOUND AND Python3_FOUND)
    include(${SWIG_USE_FILE})
    set(CMAKE_SWIG_FLAGS "")
    set_property(SOURCE swig/parking.i PROPERTY CPLUSPLUS ON)
    set_property(SOURCE swig/parking.i PROPERTY SWIG_MODULE_NAME parking)

    swig_add_library(parking
        TYPE MODULE
        LANGUAGE python
        SOURCES swig/parking.i
    )
    target_link_libraries(parking PRIVATE parking_core_shared)
    target_include_directories(parking PRIVATE ${CMAKE_SOURCE_DIR}/include)

    if(WIN32)
        set_target_properties(parking PROPERTIES SUFFIX ".pyd")
    endif()

    set(PARKING_PYTHON_DIR "${CMAKE_BINARY_DIR}/python")
    add_custom_command(TARGET parking POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${PARKING_PYTHON_DIR}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE:parking>"
            "${PARKING_PYTHON_DIR}/"
        COMMENT "Copiando modulo parking a build/python"
    )
endif()

install(TARGETS parking_server parking_generator parking_core_shared
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
)
