# Contactile

# 3D Force Button Sensor Visualisation Software (Beta v3.0)

Installation and Operation Manual 

Document #: 3DFBSVIS_B3.0_MAN_DEC24 

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

1 Introduction.. 4 

2 Safety .. . 5 

2.1 General.. 5 

2.2 Explanation of warnings .. 5 

2.3 Precautions.. 5 

3 Getting started . . 6 

3.1 Introduction . . 6 

3.2 Hardware installation... . 6 

3.3 End user licence agreement licence.. . 6 

3.4 Software installation ... 6 

4 Operation... 7 

4.1 COM Port.. 7 

4.2 Microsoft Windows display settings.. 7 

4.3 Starting the software ... 7 

4.4 Start-up sequence.. 7 

5 GUI overview ... . 8 

5.1 Visual representation of sensor force ... 8 

5.2 Force plots .. 9 

5.3 GUI controls.. . 10 

5.3.1 Changing the COM port.. . 10 

5.3.2 Biasing the sensor data . . 10 

5.3.3 Save COM port configuration.. . 10 

5.3.4 Change graph Y-axis limits . . 10 

5.3.5 Log file controls... 11 

5.3.6 Keyboard shortcuts.. 11 

6 Log file ... .. 12 

6.1 Overview... . 12 

6.2 Log file location .. . 12 

6.3 Log file name . . 12 

6.4 Log file format .. . 12 

# 1 Introduction

The 3D Force Button Sensor Development Kit (Beta v1.0) is a system of (up to) five 3D Force Button Sensors per adapter, and a DEV001 development board. Each 3D Force Button Sensor can measure 3D force. The DEV001 development board supplies power for, and coordinates the simultaneous data acquisition from, up to five 3D Force Button Sensors. The DEV001 development board is shipped with visualisation software and C++ libraries for Windows and Linux environments and a ROS node for developing software control algorithms using the sensor signals. 

Two 3D Force Button Sensors are shown in Figure 1.1, connected to a DEV001 development Board with USB-C cable. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/b6b3fafdcde2e565babcdfb621b4a9772b296e4c8e7a3dcd111ff3e1cfedc0dc.jpg)



Figure 1.1 – Two 3D Force Button Sensors connected to a DEV001 development board and USB-C cable.


This document contains an operation and installation manual for the 3D Force Button Sensor Visualisation Software (Beta v3.0). Figure 1.2 shows a screenshot of the Visualisation Software. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/666ae70fdb386086d37e7e1b128eff6fdc2cb3ba86a1a7ec718c49c0bbe5163e.jpg)



Figure 1.2 – The 3D Force Button Sensor Visualisation Software (v3.0).


# 2 Safety

# 2.1 General

The customer should verify that the maximum loads and moments expected during operation fall within the sensing range of the sensor as outside this range, sensor reading accuracy is not guaranteed (refer to Document #3DFBS_Datasheet_RevX.X). Particular attention should be paid to dynamic loads caused by robot acceleration and deceleration if the sensors are mounted on robotic equipment. These forces can be many multiples of the value of static forces in high acceleration or deceleration situations. 

# 2.2 Explanation of warnings

The warnings included here are specific to the product(s) covered by this manual. It is expected that the user heed all warnings from the manufacturers of other components used in the installation. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/132c6fb9a600bf70b25d0c2d89420d0ca24c7c4fed86f7f0002c643409479a43.jpg)


Danger indicates that a situation could result in potentially serious injury or damage to equipment. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/6be04f0006b08bd9d82becd85a9c3953ae1de5af1ed2d66f7e40969783ada10a.jpg)


Caution indicates that a situation could result in damage to the product and/or the other system components. 

# 2.3 Precautions

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/27178d6eefe904661a64da2fa0e6f90efc8a8aa3519a1b66696442240a7258a8.jpg)


DANGER: Do not attempt to disassemble the sensor. This could damage the sensor and will invalidate the calibration. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/232ee5e648796ef5d7cae6122a69c48bea362c0937cbbb65ea004666740a9f16.jpg)


DANGER: Do not attempt to drill, tap, machine, or otherwise modify the sensor casing. This could damage the sensor and will void any warranty. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/778aeeebbcde22be37c7d263605ee72f2110a0608184087acfd58ec1d074eb60.jpg)


DANGER: Do not use the sensor on abrasive surfaces or surfaces with sharp points/edges. This could damage the silicone surface of the sensor. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/f010ceb6203f08d43c3981c93046d84e7aa72ebc79213ae506c490764766c690.jpg)


CAUTION: Sensors may exhibit a small offset in readings when exposed to intense light sources. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/683baf4b9f31404117ffc9dc930252d58af95d57550c17c484867fdb37c20fe7.jpg)


CAUTION: Exceptionally strong and changing electromagnetic fields, such as those produced by magnetic resonance imaging (MRI) machines, constitute a possible source of interference with the operation of the sensor and Controller. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/bc0d799da84e98bfd75ec07e7bf2b02474e90d252206dc10c6f152225d66a6c8.jpg)


CAUTION: Temperature variations can cause drift in sensor readings. Some temperature compensation is included in the Development Kit. However, bias removal in software prior to operation is necessary, and it is recommended that biasing is performed each time the sensor is known to be unloaded. 

# 3 Getting started

# 3.1 Introduction

This section contains instructions for setting up and using 3D Force Button Sensor Visualisation Software. It is recommended that first time users first read the preceding Safety section, then read through this section to get more familiar with the system. 

# 3.2 Hardware installation

The visualisation software is used with the 3D Force Button Sensors and DEV001 board. The DEV001 board should first be connected to the sensors and then to a PC via the USB-C port on the DEV001 board before you can use the visualisation software. For more information about connecting the sensors, refer to Document #DEV001_Datasheet_Rev1.1. 

The USB-C port is shown in Error! Reference source not found.. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/5dbbcbdfffc549f3a1e00214d505107dbea96a3037532a73c8a1c41bba7b0060.jpg)



Figure 3.1 – USB-C port of the DEV001 board


# 3.3 End user licence agreement licence

Contactile's end user license agreement applies to all software and algorithms included with the products sold by Contactile. The end user license agreement that applies is provided on the USB flash drive shipped with the product in the folder ‘LEGAL’ in the root directory. 

# 3.4 Software installation

The visualisation software is provided on the Contactile USB flash drive that was shipped with the development kit. Copy the entire contents of the Contactile USB flash drive to a location on the PC running Microsoft Windows. 

# 4 Operation

A Java-based graphical user interface (GUI) is provided for basic post-installation testing and general demonstration of sensor operation. This GUI can be found on the Contactile USB flash drive which was shipped with the Development Kit. The executable file is located in the folder ‘SOFTWARE/VIS’ in the root directory. 

# 4.1 COM Port

The data transmission protocol between the Controller device and the PC is a serial connection emulated on the USB connection, visible as a COM port on the PC. After connecting the Controller to the PC, use the PCs device manager to determine the COM port number of the connection. 

# 4.2 Microsoft Windows display settings

Before starting the software, for the GUI to display in full screen, it is recommended to change the Windows display settings. In Windows 10: 

1. Type “Display Settings” in the Windows search bar 

2. Open the “Display Settings” 

3. In the section “Scale and layout”, change the “size of text, apps and other items” to “100%” 

# 4.3 Starting the software

Run the executable file “PTSVIS_Fingertip_B3.0.0.exe”. 

# 4.4 Start-up sequence

Once the software is launched, the GUI will appear. A serial connection will need to be made before the software begins sampling and displaying the data. To select a COM port and make a serial connections, see 5.3.1 Changing the COM port). 

# 5 GUI overview

The top left area of the GUI window is a visual representation of the sensor connected to the SEN0 port of the Controller, and the top right is a visual representation of the sensor connected to the SEN1 port. Directly below each sensor visual representation is an area displaying 3D force plots for each sensor. There are also numerous controls for changing the display options, connecting to the Controller, logging data, and biasing the sensors - these are highlighted in Figure 5.1. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/ea89f68b01d55b2f4d00421e515d6da52abd024eceeb33e7f325fd66de7b2597.jpg)



Figure 5.1 – GUI components of the visualisation software.


# 5.1 Visual representation of sensor force

The visual representation takes a top view of the sensor. Each sensor is represented as a 2-D grey (when unloaded) or white (when loaded) circle shape with a cross hair representing the tip of the pillar. The representation of an unloaded sensor is shown alongside the physical sensor is shown in Figure 5.2. 


Visual representation of sensor


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/dee1c16ffd084a78bd4c10c94dab2e607d7de61cb58808b108e9af49eaf21489.jpg)



Top view of real sensor


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/dde10907ec230a533bc42237c5319c2cce22b5779652bcd1c8edf9c00394a5a7.jpg)



Figure 5.2 – Visual representation of sensor in GUI, including the X and Y axis orientation; and corresponding physical sensor.


The cross hair moves up and down, and right and left to indicate positive and negative forces acting on the sensor, in the X- and Y-axis, respectively. The shape of the pillar representation deforms as a result of forces being applied in the X- and Y- axis. Additionally, Z compression of the sensor is represented by a grey circle centred at the cross-hair – larger positive Z force results in a larger grey circle. Contact is represented by a change in the colour of the pillar – when the pillar is not in contact, it is grey, and when contact is made, the pillar becomes white. For visual purposes, the default threshold for a pillar to be considered in contact is 0.2 N in any one axis. Figure 5.3 shows an unloaded pillar, a pillar that is compressed to 1.5 N in the Z-axis, a pillar compressed to 5 N in the Z-axis, and a pillar compressed to 6 N in the Z-axis and a force is applied in the positive Y-axis. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/c3328610bbdfbbf5cd892050f63eaccaf8acf240c12e759deb1b073fef7a24bf.jpg)



Figure 5.3 – Visual representation of a sensor when uncompressed, compressed to different zforces, and under Y-axis force.


# 5.2 Force plots

For each pillar, the calibrated X-, Y- and Z-axis forces vs. time are displayed in their respective plots. The relative locations of the force vs. time plots correspond to the pillar location in the sensor visualisation. The X-axis force is displayed as a yellow trace, the Y-axis force is displayed as a green trace, and the Z-axis force is displayed as a blue trace. Figure 5.4 shows a force vs. time plot for a sensor. The time axis is 1-s per division. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/2b364ad98fa2618eaa5e6d4adc6010153ea50b7b70b3dc0f33a648998e24778f.jpg)



Figure 5.4 – Force vs. time plot. The X-axis force is displayed in yellow, the Y-axis force is displayed in green, and the Z-axis force is displayed in blue.


# 5.3 GUI controls

# 5.3.1 Changing the COM port

The GUI controls related to the serial connection are shown in Figure 5.5. To change the COM port number of the serial connection to the Controller: 

1. If the GUI is already connected to a COM port, click the Disconnect button. 

2. Click on the Refresh button to refresh the list of available COM ports. 

3. Select the appropriate COM port number from the COM Port drop down list. 

4. Click on the Connect button. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/f17b10fc1231a0bd669fd89e95b665cc943d62e8bf9949f8461c1cf350cefe97.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/a1d27d7d03a989f8a6a104fa543c63af8fcaa220011ae12f3b78cda97c9cfe79.jpg)



Figure 5.5 – Changing the COM port in the GUI and connecting


# 5.3.2 Biasing the sensor data

To bias the data (i.e., remove any offset in the calibrated force data when the sensor is unloaded), ensure that the sensor is unloaded and the signals are in a steady state, click on the Bias Sensors button (Figure 5.6). The bias operation takes approximately 2 s. Ensure that the sensor remains unloaded throughout this time. The sensor calibrated force signals should become zero after this point. 

# Bias Sensors

Figure 5.6 – Biasing the sensors 

# 5.3.3 Save COM port configuration

To save the default COM port, first select the COM port from the drop down menu (see section 5.3.1 Changing the COM port), then select the Save Config button (see Figure 5.7). 

# Save Config

Figure 5.7 – Save Config button 

# 5.3.4 Change graph Y-axis limits

To increase the force-axis resolution (i.e., reduce the limits of the force-axis) of the force vs. time plots, click on the Toggle Force Y-Range button (see Figure 5.8). Each time the Toggle Force Y-Range button is pressed, the force-axis limits will reduce, until the minimum limit of ±0.5 N. If the force-axis limits are ±0.5 N and the Toggle Force Y-Range button is pressed, then the force-axis limits will reset to the maximum limit of ±10 N. 

# Toggle Force Y-Range

Figure 5.8 – Toggle Force Y-Range button 

# 5.3.5 Log file controls

The log file controls are shown in Figure 5.9. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/831734de513bfa772abf4b6b200821e7d1d1dfaa47351b7e3bd05fa9c2435601.jpg)



Figure 5.9 – Log file controls


# 5.3.5.1 Changing the log file rate

To change the log file sampling rate, select the appropriate rate from the-drop down list next to Logging Rate. The log file sampling rate can only be changed when the GUI is not logging data. 

# 5.3.5.2 Start/stop logging

To start logging data, click on the Start Log button. If data logging had previously been started, click on the Stop Log button to stop logging and save the log file – see section 6 Log file for more information about the log file. 

# 5.3.6 Keyboard shortcuts

A list of keyboard shortcuts is displayed in the GUI. These are shown in Figure 5.10. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/70e0fcb9-3bc8-40f6-89fb-fedc64630762/7820b289752acd1a3fb85fb3c11e10181018e0334407c4362e669db7fbc1aee7.jpg)



Figure 5.10 – List of keyboard shortcuts displayed in the GUI


# 6 Log file

# 6.1 Overview

The visualisation software can generate a log file of the sensor data. 

# 6.2 Log file location

The log file is stored in the Logs subfolder in the same location as the Visualisation Software executable file which was run to launch the GUI. 

# 6.3 Log file name

The name of the log file that is generated is LOG_YYMMDD_hhmmss.csv where YY is the two digit year, MM is the two digit month, DD is the two digit day, hh is the two digit hour, mm is the two digit minute and ss is the two digit second from the system clock at the time that the log file was created. 

# 6.4 Log file format

The log file is saved as comma-separated values (CSV) in ASCII text format. The order of the values and a description is shown in Table 6.1. 


Table 6.1 – Data in log file


<table><tr><td>Data Order</td><td>Data Name</td><td>Data Description</td><td></td></tr><tr><td>1</td><td>T_us</td><td>Timestamp in μs</td><td>Timestamps</td></tr><tr><td>2</td><td>S0_G_FX</td><td>Sensor 0, X-axis force in Newtons</td><td rowspan="3">Sensor 0, forces</td></tr><tr><td>3</td><td>S0_G_FY</td><td>Sensor 0, Y-axis force in Newtons</td></tr><tr><td>4</td><td>S0_G_FZ</td><td>Sensor 0, Z-axis force in Newtons</td></tr><tr><td colspan="4">⋮</td></tr><tr><td>29</td><td>S4_G_FX</td><td>Sensor 4, X-axis force in Newtons</td><td rowspan="3">Sensor 4, forces</td></tr><tr><td>30</td><td>S4_G_FY</td><td>Sensor 4, Y-axis force in Newtons</td></tr><tr><td>31</td><td>S4_G_FZ</td><td>Sensor 4, Z-axis force in Newtons</td></tr></table>

S0, refers to the sensor connected to PORT 0, S1 refers to the sensor connected to PORT 1, and so on, and S4 refers to the sensor connected to PORT 4 of the DEV0001 development. 

If a sensor is not connected, the log file will contain values of 0.0 for FX, FZ and FZ in the corresponding data columns. 