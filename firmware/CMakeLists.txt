cmake_minimum_required(VERSION 3.13)

# Include Raspberry Pi Pico SDK
include(pico_sdk_import.cmake OPTIONAL)

project(pc_usb_bridge C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Raspberry Pi Pico SDK if found
if (COMMAND pico_sdk_init)
    pico_sdk_init()
endif()

add_executable(pc_usb_bridge
    src/main.c
    src/ft245_bus.c
    src/power_monitor.c
    src/protocol.c
)

target_include_directories(pc_usb_bridge PRIVATE
    include
)

# Compile options for strict safety
target_compile_options(pc_usb_bridge PRIVATE
    -Wall
    -Wextra
    -Werror
    -O2
)

if (COMMAND pico_add_extra_outputs)
    target_link_libraries(pc_usb_bridge
        pico_stdlib
        hardware_pio
        hardware_dma
        hardware_i2c
        hardware_watchdog
    )
    pico_add_extra_outputs(pc_usb_bridge)
endif()
