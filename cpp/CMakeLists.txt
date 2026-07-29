cmake_minimum_required(VERSION 3.0...3.5)

project(
    Kufar-Telegram-Notifier-by-Mihalkin
    VERSION 3.0.0
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../bin)

add_executable(
    Kufar-Telegram-Notifier
    
    src/logger.cpp
    src/kufar.cpp
    src/helperfunctions.cpp
    src/telegram.cpp
    src/networking.cpp
    src/main.cpp
)

target_include_directories(
    Kufar-Telegram-Notifier
    PRIVATE
    include
)

target_compile_options(
    Kufar-Telegram-Notifier
    PRIVATE
    -Wall
    -Wextra
)

target_link_libraries(Kufar-Telegram-Notifier curl)
