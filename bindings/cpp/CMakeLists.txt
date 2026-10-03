cmake_minimum_required(VERSION 3.24)
project(RadrootsCpp VERSION 0.0.0 LANGUAGES C CXX)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CTest)
find_package(Radroots CONFIG REQUIRED)
set(RADROOTS_VERSION "${PROJECT_VERSION}" CACHE STRING "SDK version")
configure_package_config_file(cmake/RadrootsCppConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppConfig.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/RadrootsCpp"
    PATH_VARS CMAKE_INSTALL_INCLUDEDIR)
configure_file(cmake/RadrootsCppTargets.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppTargets.cmake" @ONLY)
write_basic_package_version_file("${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppConfigVersion.cmake"
    VERSION "${RADROOTS_VERSION}" COMPATIBILITY SameMajorVersion)
install(DIRECTORY include/ DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppTargets.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/RadrootsCppConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/RadrootsCpp")
install(FILES LICENSE-MIT LICENSE-APACHE DESTINATION "${CMAKE_INSTALL_DATADIR}/radroots-cpp")
file(READ README.md RADROOTS_README)
string(REPLACE "../../DEVELOPERS.md" "DEVELOPERS.md" RADROOTS_README "${RADROOTS_README}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/README.md" "${RADROOTS_README}")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/README.md" ../../DEVELOPERS.md
    DESTINATION "${CMAKE_INSTALL_DATADIR}/radroots-cpp")
if(BUILD_TESTING)
    find_package(Threads REQUIRED)
    foreach(linkage IN ITEMS shared static)
        add_executable(cpp_api_${linkage} tests/api.cpp)
        target_include_directories(cpp_api_${linkage} PRIVATE include)
        target_compile_features(cpp_api_${linkage} PRIVATE cxx_std_17)
        target_compile_options(cpp_api_${linkage} PRIVATE -Wall -Wextra -Werror -UNDEBUG)
        target_link_libraries(cpp_api_${linkage} PRIVATE Radroots::c_${linkage} Threads::Threads)
        add_test(NAME cpp_api_${linkage} COMMAND cpp_api_${linkage})
    endforeach()
    add_executable(cpp_no_exceptions tests/no_exceptions.cpp tests/status_stub.c)
    target_include_directories(cpp_no_exceptions PRIVATE include "${RADROOTS_INCLUDE_DIR}")
    target_compile_features(cpp_no_exceptions PRIVATE cxx_std_17 c_std_11)
    target_compile_options(cpp_no_exceptions PRIVATE -Wall -Wextra -Werror -UNDEBUG "$<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>")
    target_compile_definitions(cpp_no_exceptions PRIVATE RADROOTS_STATIC)
    add_test(NAME cpp_no_exceptions COMMAND cpp_no_exceptions)
endif()
