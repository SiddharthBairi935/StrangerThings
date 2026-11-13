cmake_minimum_required(VERSION 3.20)
project(lucas_cpp_smoke LANGUAGES C CXX)

enable_testing()
add_executable(lucas_cpp_test tests/test_main.cpp)
target_compile_features(lucas_cpp_test PRIVATE cxx_std_17)
add_test(NAME calculator_adds_two_numbers COMMAND lucas_cpp_test)

add_executable(lucas_c_test tests/test_c.c)
add_test(NAME c_calculator_adds_two_numbers COMMAND lucas_c_test)