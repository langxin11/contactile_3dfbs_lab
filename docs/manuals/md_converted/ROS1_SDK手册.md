# Contactile

# 3D Force Button Sensor ROS

# (Beta v1.0)

# Installation and Operation Manual

Document #: 3DFBSROS_B1.0_MAN_DEC24 

December, 2024 

# Foreword

Information contained in this document is the property of Contactile Pty Ltd. and shall not be reproduced in whole or in part without prior written approval of Contactile Pty Ltd. The information herein is subject to change without notice and should not be construed as a commitment on Contactile Pty Ltd. This manual is periodically revised to reflect and incorporate changes made to the 3D Force Button Sensor Development Kit. 

Contactile Pty Ltd assumes no responsibility for any errors or omissions in this document. Users' critical evaluation is welcome to assist in the preparation of future documentation. 

Copyright © by Contactile Pty Ltd, Sydney, Australia. All Rights Reserved. 

Published in Australia. 

All trademarks belong to their respective owners. 

# Conditions of Sale

Contactile's conditions of sale apply to all products sold by Contactile to the Distributor under this Agreement. The conditions of sale that apply are provided on the USB flash drive shipped with the product in the folder ‘LEGAL’ in the root directory. 

# End User Licence Agreement

Contactile's end user license agreement applies to all software and algorithms included with the products sold by Contactile. The end user license agreement that applies is provided on the USB flash drive shipped with the product in the folder ‘LEGAL’ in the root directory. 

# Compliance

The devices are sold as is. 

The devices are specifically designed solely for the purposes of research and development only made available on a business-to-business basis. 

The devices are not for resale. 

# Table of Contents

1 Introduction ..... 4 

2 Safety .. 5 

2.1 General . 5 

2.2 Explanation of warnings. 5 

2.3 Precautions .. 5 

3 Getting started . . 6 

3.1 Hardware installation .. 6 

3.2 Minimum requirements . 6 

3.3 ROS node location ... 6 

4 Package summary .. 7 

5 Installing the package.. 7 

6 Starting the node.. 7 

7 buttonsensor_ros_node.. . 8 

7.1 Parameters 8 

7.2 Subscribed topics . 8 

7.3 Messages... 9 

7.4 Services.. 9 

7.5 Log file .. . 10 

# 1 Introduction

The 3D Force Button Sensor Development Kit (Beta v1.0) is a system of (up to) five 3D Force Button Sensors per adapter, and a DEV001 development board. Each 3D Force Button Sensor can measure 3D force. The DEV001 development board supplies power for, and coordinates the simultaneous data acquisition from, up to five 3D Force Button Sensors. The DEV001 development board is shipped with visualisation software and C++ libraries for Windows and Linux environments and a ROS node for developing software control algorithms using the sensor signals. 

Two 3D Force Button Sensors are shown in Figure 1.1, connected to a DEV001 development Board with USB-C cable. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/97f4e7c8719877e692c18a24c7b682aa861910946742ad630e953f01640d60ea.jpg)



Figure 1.1 – Two 3D Force Button Sensors connected to a DEV001 development board and USB-C cable.


This document is an installation and operation manual for the ROS Node which was provided on the Contactile USB flash drive that was shipped with the 3D Force Button Sensor and DEV001 development board. 

# 2 Safety

# 2.1 General

The customer should verify that the maximum loads and moments expected during operation fall within the sensing range of the sensor as outside this range, sensor reading accuracy is not guaranteed (refer to Document #3DFBS_Datasheet_RevX.X). Particular attention should be paid to dynamic loads caused by robot acceleration and deceleration if the sensors are mounted on robotic equipment. These forces can be many multiples of the value of static forces in high acceleration or deceleration situations. 

# 2.2 Explanation of warnings

The warnings included here are specific to the product(s) covered by this manual. It is expected that the user heed all warnings from the manufacturers of other components used in the installation. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/6b642c4ebb6b1050e32065e45b0a2eeff3eee871a6541bd89ca5ed2f57a56fab.jpg)


Danger indicates that a situation could result in potentially serious injury or damage to equipment. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/fa73aed1dc0618a6f3ba4a18bb1b20848b966e69d865e1d10444c640d9862be5.jpg)


Caution indicates that a situation could result in damage to the product and/or the other system components. 

# 2.3 Precautions

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/71b378f654de6aa60b2bc093ad4d1232c01689652f6d7679446d8632c4acd40e.jpg)


DANGER: Do not attempt to disassemble the sensor. This could damage the sensor and will invalidate the calibration. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/af80c53d321379bb201cae72394cd09d8b4c843c0d20f278f84cc44271aa6370.jpg)


DANGER: Do not attempt to drill, tap, machine, or otherwise modify the sensor casing. This could damage the sensor and will void invalidated the calibration. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/eb0af063e590a70028cd4758ae2a03ff1066767e9f06112b9291fdffb75fd463.jpg)


DANGER: Do not use the sensor on abrasive surfaces or surfaces with sharp points/edges. This could damage the silicone surface of the sensor. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/524d0b475b47d378d9eb2920c90157456566d5f5eb82076e52e8781f2a528417.jpg)


CAUTION: Sensors may exhibit a small offset in readings when exposed to intense light sources. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/ad6636db659ba72e0ccd9daf767a92daca606bf779b5fc372593e7175407bc3a.jpg)


CAUTION: Exceptionally strong and changing electromagnetic fields, such as those produced by magnetic resonance imaging (MRI) machines, constitute a possible source of interference with the operation of the sensor and Controller. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/6bea1a77-303c-4ca2-b3d0-79690b2ad60c/e4a76c01b791ccfdf8457ac07769afb7ad521c90a6a4ed548cf919d678a11685.jpg)


CAUTION: Temperature variations can cause drift in sensor readings. Some temperature compensation is performed. However, bias removal in software prior to operation is necessary, and it is recommended that biasing is performed each time the sensor is known to be unloaded. 

# 3 Getting started

This section contains instructions for setting up and using 3D Force Button Sensor C++ Library for WINDOWS (Beta v1.0). It is recommended that first time users first read the preceding Safety section, then read through this section to get more familiar with the system. 

# 3.1 Hardware installation

The ROS node is used with the 3D Force Button Sensors and DEV001 board. The DEV001 board should first be connected to the sensors and then to a PC via the USB-C port on the DEV001 board before you can use the visualisation software. For more information about connecting the sensors, refer to Document #DEV001_Datasheet_Rev1.1. 

# 3.2 Minimum requirements

The ROS node has been tested on a HP EliteBook with the following specifications 

CPU: Intel Core i7 -4600U 

▪ RAM: 16 GB RAM 

Operating System: Ubuntu 20.04.2.0 LTS 

▪ ROS installation: noetic 

# 3.3 ROS node location

The ROS node is provided on the Contactile USB flash drive that was shipped with the development kit in the folder named SOFTWARE/ROS. The ROS node is the buttonsensor_ros_v1 subfolder. The files in the ROS/buttonsensor_ros_v1 folder are summarised in Table 3.1. 


Table 3.1 – Files in ROS/buttonsensor_ros_v1 folder


<table><tr><td>Sub Folder</td><td>File Name</td><td>File Description</td></tr><tr><td>.</td><td>CMakeLists.txt</td><td>Directives and instructions describing the project&#x27;s source files and targets</td></tr><tr><td>.</td><td>package.xml</td><td>The package manifest</td></tr><tr><td>.</td><td>README.md</td><td>Readme file</td></tr><tr><td>include</td><td>buttonsensor_ros_node.hpp</td><td>The header file for the node</td></tr><tr><td>launch</td><td>buttonsensor.launch</td><td>A launch file</td></tr><tr><td>lib</td><td>libPTSDK.aPTSDKListener.hPTSDKSensor.hPTSDKPillar.hPTSDKConstants.h</td><td>The C++ library and associated header files</td></tr><tr><td>msg</td><td>ButtonSensorState.msg</td><td>Message definitions of the ButtonSensorState message</td></tr><tr><td>src</td><td>buttonsensor_ros_node.cpp</td><td>The cpp file for the node</td></tr><tr><td>srv</td><td>BiasRequest.srv</td><td>Service definition of the BiasRequest service</td></tr></table>

# 4 Package summary

This package implements a driver for the 3D Force Button Sensor Development Kit (Beta v1.0). 

Maintainer status: maintained 

Maintainer: Heba Khamis (Contactile) <heba DOT khamis AT contractile DOT com> 

Author: Heba Khamis 

License: LGPLv3 

The buttonsensor_ros_v1 package provides a ROS interface that publishes data from ten 3D Force Button Sensors connected to a Controller that is connected over USB. The package allows the following: 

1. Connecting to the controller, sampling the sensors at 100, 500 or 1000 Hz and publishing the data 

2. Biasing the sensors 

3. Starting and stopping slip detection on the Controller 

# 5 Installing the package

To use this package you should have ROS up and running. To install the package copy the buttonsensor_ros_v1 folder into the src folder of your catkin workspace. 

# 6 Starting the node

The buttonsensor.launch launch file is provided to configure the COM port connection, get data from the sensors and publish the data. 

# 7 buttonsensor_ros_node

ROS-Node for connecting to the controller and publishing sensor data. 

# 7.1 Parameters


Table 7.1 – Parameters of the buttonsensor_ros_v1 node


<table><tr><td>Name</td><td>Type</td><td>Description</td></tr><tr><td>hub_id</td><td>int</td><td>Identifier for the Controller</td></tr><tr><td>n_sensors</td><td>int</td><td>Number of sensors connected to the Controller. Should be 10.</td></tr><tr><td>com_port</td><td>string</td><td>Name of the COM port. Usually /dev/ttyACM0.</td></tr><tr><td>baud_rate</td><td>int</td><td>Baud rate for the serial connection to the Controller. Should be 9600.</td></tr><tr><td>parity</td><td>int</td><td>Parity of the serial connection to the Controller. Should be 0.</td></tr><tr><td>byte_size</td><td>int</td><td>Size of a byte. Should be 8.</td></tr><tr><td>log_file_rate</td><td>int</td><td>Log file rate of the Controller. Options: 100, 500 or 1000 (Hz)</td></tr></table>

NB: Even though, only five 3DFB Sensors can be connected to the DEV001 development board, n_sensors must be 10 for backward compatibility with the older analogue 3D Force Button Sensors. 

# 7.2 Subscribed topics

/hub_0/sensor_0 (See SensorState message) 

• Publish sensor data from Sensor 0 connected to the DEV001 development board (PORT 0) 

/hub_0/sensor_1 (See SensorState message) 

• Publish sensor data from Sensor 1 connected to the DEV001 development board (PORT 0) 

/hub_0/sensor_4 (See SensorState message) 

• Publish sensor data from Sensor 4 connected to the DEV001 development board (PORT 4) 

NB: The following topics also exist, but these will contain data equal to zero – these are required for backward compatibility with the older analogue 3D Button Force Sensor: 

/hub_1/sensor_5 (See SensorState message) 

/hub_1/sensor_6 (See SensorState message) 

/hub_1/sensor_9 (See SensorState message) 

# 7.3 Messages

# 7.3.1 ButtonSensorState message


Table 7.2 – Variables in the ButtonSensorState message


<table><tr><td>Parameter</td><td>Description</td></tr><tr><td>Header header</td><td></td></tr><tr><td>int64 tus</td><td>The time in μs on the Controller of this sample</td></tr><tr><td>float32 gfX</td><td>The global X-force of the sensor</td></tr><tr><td>float32 gfY</td><td>The global Y-force of the sensor</td></tr><tr><td>float32 gfZ</td><td>The global Z-force of the sensor</td></tr></table>

# 7.4 Services


Table 7.3 – Services of the buttonsensor_ros_v1 node


<table><tr><td>Name</td><td>Description</td></tr><tr><td>SendBiasRequest</td><td>■ Biasing refers to removing any offset in the sensor readings when the sensors are unloaded.■ It is recommended that the user performs a bias each time the sensors are known to be unloaded.■ Ensure that the sensor has been unloaded for at least one second before performing a bias to ensure that the bias calculation does not include hysteresis effects. A bias operation can take up to two seconds. Ensure that the sensor remains unloaded throughout this time.</td></tr></table>

# 7.5 Log file

# 7.5.1 Overview

In the buttonsensor_ros_v1/src/buttonsensor_ros_node.cpp file (line 3) a PTSDKListener object (listener_) is initialised with a boolean argument that specifies whether to log data to a .csv file or not. The argument can be changed to true (to enable logging) or false (to disable logging), remembering that the node should be remade by a call to the catkin_make utility. 

# 7.5.2 Log file location

If logging is enabled, then a .csv log file will be generated and saved in the location /home/.ros/Logs. 

NB: The .ros folder is a hidden location – make sure that you can view hidden files. 

# 7.5.3 Log file name

The name of the log file that is generated is LOG_YYYY_MM_DD_hh_mm_ss.csv where: 

• YYYY is the four digit year, 

MM is the two digit month, 

DD is the two digit day, 

hh is the two digit hour, 

mm is the two digit minute and 

ss is the two digit second, 

from the system clock at the time that the log file was created. 

# 7.5.4 Log file format

The log file is saved as comma-separated values (CSV) in ASCII text format. The order of the values and a description is shown in Table 7.4. 


Table 7.4 – Data in log file


<table><tr><td>Data Order</td><td>Data Name</td><td>Data Description</td><td></td></tr><tr><td>1</td><td>T_us</td><td>Timestamp in μs</td><td>Timestamps</td></tr><tr><td>2</td><td>S0_G_FX</td><td>Sensor 0, X-axis force in Newtons</td><td rowspan="3">Sensor 0, forces</td></tr><tr><td>3</td><td>S0_G_FY</td><td>Sensor 0, Y-axis force in Newtons</td></tr><tr><td>4</td><td>S0_G_FZ</td><td>Sensor 0, Z-axis force in Newtons</td></tr><tr><td colspan="4">⋮</td></tr><tr><td>29</td><td>S9_G_FX</td><td>Sensor 9, X-axis force in Newtons</td><td rowspan="3">Sensor 9, forces</td></tr><tr><td>30</td><td>S9_G_FY</td><td>Sensor 9, Y-axis force in Newtons</td></tr><tr><td>31</td><td>S9_G_FZ</td><td>Sensor 9, Z-axis force in Newtons</td></tr></table>

S0, refers to the sensor connected to PORT 0, S1 refers to the sensor connected to PORT 1, and so on, and S4 refers to the sensor connected to PORT 4 of the DEV0001 development. 

NB: S5 to S9 sensors will have all data equal to zero – these are necessary for backward compatibility with the older analogue 3D Force Button Sensor. 

If a sensor is not connected, the log file will contain values of 0.0 for FX, FZ and FZ in the corresponding data columns. 