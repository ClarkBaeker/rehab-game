# Rehab Game

Explaining the Rehab Game

Communication via websocket

## Project Structure

The structure of this project is a single repo containing three subprojects for the three different components of the game:
1. The Computer running PyGame (`/pygame-app`)
2. The ESP32 controlling the LEDs on the blackboard (`esp32-firmware-board`)
3. The ESP32 driving the vibromotors (`esp32-firmware-knee`)

The `/pygame-app` is a python project while `esp32-firmware-board` and `esp32-firmware-knee` are PlatformIO projects.

```
rehab-game
│   README.md
│
└───pygame-app
│   │   main.py
│   
└───esp32-firmware-board
│   │
│   └───src
│   │   │   main.cpp
│   │   platform.ini
│   └───include
│   │   │   wifi_credentials.h.template
│   └───...
│
└───esp32-firmware-knee
│   │
│   └───src
│   │   │   main.cpp
│   │   platform.ini
│   └───include
│   │   │   wifi_credentials.h.template
│   └───...
```

## Setup

When starting the game, the two ESPs need to be connected to the same local WIFI as the computer running the `/pygame-app`. To prepare them for that, follow these steps:
1. Copy the two content of the template file for the wifi credentials that you find in the `/<esp_project>/include` folder of each ESP-project to a header file `/<esp_project>/include/wifi_credentials.h`.
2. In these files enter the WIFI credentials of the WIFI that the computer running the `/pygame-app` is connected to.
3. Additionally, you need to add the ip address of the computer running the `/pygame-app`.  

The `wifi_credentials.h` file is part of `.gitignore` and thereby the credentials kept safe locally.

Next, you can startup the `/pygame-app` by running `main.py`. This will also start the websocket server that the two ESPs attached to the blackboard and knee will connect to as clients.

Lastly, upload the `esp32-firmware-board` and `esp32-firmware-knee` firmware onto the ESP32 boards by running the **Upload and Monitor** option of PlatformIO.

Everything is set up - Have fun!


