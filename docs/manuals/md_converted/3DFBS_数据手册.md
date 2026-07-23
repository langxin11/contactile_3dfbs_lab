# Product Overview

The 3D Force Button Sensor is designed for precise measurement of forces applied to the sensor in three dimensions – X, Y shear, and Z compression (as per the drawing on the right). Constructed with an anodized, machined aluminum housing and a silicone rubber contact surface, this sensor offers accuracy and reliability in diverse force-sensing applications. 

The sensor is interfaced via an 8-way, 0.5mm pitch FPC cable, and mechanically mounted with two M1.6 screws. 

The 3DFBSxx family contains devices with three different calibrated force ranges and measurement resolutions (N): 

<table><tr><td>Code</td><td>X, Y Range (N)</td><td>Z Range (N)</td><td>Resolution (N)</td></tr><tr><td>3DFBS04</td><td>±4</td><td>0 – 4</td><td>±0.005</td></tr><tr><td>3DFBS12</td><td>±8</td><td>0 – 12</td><td>±0.010</td></tr><tr><td>3DFBS20</td><td>±12</td><td>0 – 20</td><td>±0.010</td></tr></table>

Other calibrated ranges are available on request. 

# Applications

▪ Robotic and prosthetic grippers 

▪ Robotic hands and feet 

▪ Industrial automation 

Gloves for augmented reality 

▪ Rehabilitation tools 

▪ Gaming controllers 

# Features

Measure 3D applied forces up to 20 N 

▪ I2C and SPI communication interfaces 

▪ Sample rate up to 1 kHz 

▪ Compact form factor: 14.0 (W) x 19.0 (L) x 8.9 (H) mm 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/1c3540805f8040c87be3afb400b41760005c8310cd229f5448b1e57bf7c74125.jpg)


# Contents

# 1 Description .. 4

1.1 Overview... 4 

1.2 Data Output .. 4 

1.3 Modes of operation . 4 

1.3.1 Idle Mode . 4 

1.3.2 Active Mode .. 4 

1.3.3 Mode Switching.. 4 

2 Getting Started .. .. 5 

3 Absolute Maximum Ratings.. .. 6 

4 Electrical Characteristics . .. 6 

5 Pinout.. ... 6 

6 Mechanical Drawing .. 

7 Communication .. .. 8 

7.1 Interface Bootstrapping.. . 8 

7.2 Protocol . . 8 

7.3 Flash Write Commands . . 8 

7.4 Interrupts . 9 

7.5 I2C Interface ... . 9 

7.5.1 Command Phase... .9 

7.5.2 Data Exchange Phase.. ..10 

7.5.3 Active Mode Read.. ..10 

7.6 SPI Interface .. . 10 

7.6.1 Command and Data Exchange.. ...10 

7.6.2 Active Mode Read.. .11 

8 Command List .. ..12 

9 Command Descriptions .. .. 13 

9.1 NOP.. . 13 

9.2 Get Status.. 13 

9.3 Get Data . . 13 

9.4 Get Temperature . . 13 

9.5 Get Version.. . 14 

9.6 Set Active Frequency.. . 14 

9.7 Get Active Frequency .. . 14 

9.8 Set Active Data.. . 14 

9.9 Get Active Data.. . 14 

9.10 Enter Active.. . 15 

9.11 Bias Sensor... . 15 

9.12 Set I2C Address... . 16 

9.13 Who Am I ... . 16 

9.14 Set Comms Mode .. . 16 

10 Important Notes... .17 

10.1 Communication Check .. 17 

10.2 Address Collision ... 17 

10.3 Data Exchange Phase ... 17 

11 Revision History .. .17 

12 Resources. .17 

# 1 Description

# 1.1 Overview

The Contactile 3DFBS is a complete 3 axis force measurement system. It uses a silicone pillar paired with an optical sensor and a digital circuit to measure these physical characteristics. Each sensor is precalibrated to convert physical movement on the pillar to corresponding force measurements. The sensor communicates with a host system via an I2C or SPI interface. 

# 1.2 Data Output

The 3DFBS provides the following data: 

• Force applied to the sensor the in X, Y, and Z axes in newtons 

• On-board temperature in degrees Celsius 

# 1.3 Modes of operation

The sensor can operate in 2 modes, Idle and Active. 

# 1.3.1 Idle Mode

This is the default mode after a sensor reset. All commands are issued in Idle mode. To read data in idle mode, the corresponding command must be issued to the sensor followed by a data phase. Communication in idle mode has an associated overhead. 

# 1.3.2 Active Mode

Active mode minimizes communication overhead and should be used when the host wants to stream data from the sensor. After entering Active mode, the sensor processes force and temperature data at the ‘Active Frequency’. The host can simply read the corresponding number of bytes as set by the ‘Set Active Data’ command. The latest sensor data are sent to the host during a read. 

# 1.3.3 Mode Switching

To enter Active mode, the host issues the ‘Enter Active’ command. The sensor will automatically exit Active mode and return to Idle mode when any command is issued. 

# 2 Getting Started

After a reset, the sensor starts in Idle mode. All communication with the sensor should be performed using the communication interface (I2C/SPI) assigned with Interface Bootstrapping, or the ‘Set Comms Mode’ command. The factory default communication interface is SPI. 

Before the sensor can be used for any accurate readings, the ‘Bias Sensor’ command must be issued. This command should be called when no forces are being applied to the sensor, and has the effect of setting all force values to zero – similar to how a weighing scale is tared. 

After biasing, the ‘Get Data’ command can be called to retrieve sensor data. Note that without biasing, this command may return NaN values or other incorrect data. 

Before entering Active mode, the host should configure which data are to be read during every transaction, by issuing the ‘Set Active Data’ command. For example, sending ‘0x0000 0E00’ will configure the sensor to return processed force data for all 3 axes. Consequently, in Active mode, each read transaction should consist of 12 bytes. 

The sensor automatically exits Active mode and returns to Idle mode when any command is issued. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/60e42a10204327659f31fdff32aa2a74f3d9d626c29db9261c4a3bbb4e7a6f1b.jpg)


See section 9 Command Descriptions for more details on sending these commands. 


3 Absolute Maximum Ratings


<table><tr><td>Property</td><td>Absolute Maximum Ratings</td><td>Units</td></tr><tr><td><eq>V_{cc}</eq></td><td>-0.3 to +3.63</td><td>V</td></tr><tr><td>RST, INT</td><td>-0.3 to <eq>V_{cc}</eq> + 0.3</td><td>V</td></tr><tr><td>Output Current (sink) by RST, INT pins</td><td>25</td><td>mA</td></tr><tr><td>GND</td><td>100</td><td>mA</td></tr><tr><td>Operating Temperature</td><td>-40 to +105</td><td>°C</td></tr><tr><td>Compressive Force (Z)</td><td>100</td><td>N</td></tr><tr><td>Shear Force (X,Y)</td><td>50</td><td>N</td></tr></table>


* Exposure to absolute maximum rating conditions for extended periods may affect device reliability. 



4 Electrical Characteristics


<table><tr><td>Parameter</td><td>Symbol</td><td>Min</td><td>Typical</td><td>Max</td><td>Units</td></tr><tr><td>Supply Voltage</td><td><eq>V_{CC}</eq></td><td>2.6</td><td>3.3</td><td>3.6</td><td>V</td></tr><tr><td>GPIO Input Low</td><td><eq>V_{IL}</eq></td><td>-</td><td>-</td><td>0.3 x <eq>V_{CC}</eq></td><td>V</td></tr><tr><td>GPIO Input High</td><td><eq>V_{IH}</eq></td><td>0.7 x <eq>V_{CC}</eq></td><td>-</td><td>-</td><td>V</td></tr></table>


5 Pinout


<table><tr><td>Pin</td><td>Name</td><td>Description</td><td>Direction</td></tr><tr><td>1</td><td>GND</td><td>Connect to system ground.</td><td>N/A</td></tr><tr><td>2</td><td><eq>V_{cc}</eq></td><td>Connect to 3V3</td><td>N/A</td></tr><tr><td>3</td><td><eq>\overline{RESET}</eq></td><td>Active low reset. The sensor has a 100k pull-up resistor connected to this pin.</td><td>Input</td></tr><tr><td>4</td><td>MOSI</td><td>SPI Master Out Slave In</td><td>Input</td></tr><tr><td>5</td><td>MISO</td><td>SPI Master In Slave Out</td><td>Output</td></tr><tr><td>6</td><td>SCL / SCK</td><td><eq>I^{2}C</eq> Serial Clock / SPI clock</td><td>Input</td></tr><tr><td>7</td><td>SDA / <eq>\overline{CS}</eq></td><td><eq>I^{2}C</eq> Serial Data / SPI Chip Select</td><td>Input/Output</td></tr><tr><td>8</td><td>INT</td><td>Interrupt</td><td>Output</td></tr></table>


6 Mechanical Drawing


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/113867cf8f041ece129fe74b704e2595124f917491b5ba6d95cf25c5ce4735c7.jpg)



Detail: Retaining notch


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/2156c4dcf0c92e850adca26fa6d8a7230c215f65ec96e8d20a659915e04d9450.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/5ea45087b2d4deb36ef5b30a8bfa908d43a2db8580244b2c21b5f5ffe83d8007.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/7a3f86e03e504c166a68f61fbfc6bafdb209622bcbbdb97b4319bba3ed1ad4d3.jpg)



All units in millimeters.



* FPC connector conforms to Molex FFC specification PS-15266-001


# 7 Communication

# 7.1 Interface Bootstrapping

The communication interface (I2C/SPI) may be changed immediately following a device reset. 

To change the communication interface, the host must: 

• Set the ̅RESET ̅̅̅̅̅̅̅̅̅ pin LOW for at least 50ms to shutdown the sensor. 

Hold the INT pin LOW. 

• Set the ̅RESET ̅̅̅̅̅̅̅̅̅ pin HIGH to enable the sensor. 

• Wait 50ms for the sensor to start-up. With the INT pin held LOW it will enter bootstrapping mode. 

• The state of the SDA/̅CS̅̅̅ and SCL/SCK pins are then used to set the desired communication interface according to the logic table below. 

<table><tr><td>INT</td><td>SCL/SCK</td><td>SDA/CS</td><td>Communication Interface</td></tr><tr><td>HIGH</td><td>x</td><td>x</td><td>Unchanged</td></tr><tr><td>LOW</td><td>LOW</td><td>LOW</td><td><eq>I^{2}C</eq></td></tr><tr><td>LOW</td><td>LOW</td><td>HIGH</td><td>SPI</td></tr><tr><td>LOW</td><td>HIGH</td><td>LOW</td><td>Unchanged</td></tr><tr><td>LOW</td><td>HIGH</td><td>HIGH</td><td>Unchanged</td></tr></table>

• Set the INT pin HIGH again within three seconds to lock-in the desired communication interface. 

• Wait at least 30ms to allow the new communication interface to be saved before issuing any commands. 

• If the INT pin remains LOW for more than three seconds, the sensor will boot as normal, using the last saved communication interface. 

• If the INT pin is HIGH on start-up (default), the sensor will boot immediately without entering bootstrapping mode. 

The communication interface is persistent, so this operation does not need to be performed every time the sensor is powered on. 

The communication interface may also be changed using the ‘Set Comms Mode’ command, sent via the currently active communication interface. 

# 7.2 Protocol

All communication is performed in two phases: a command phase whereby a command byte is sent from the host to the sensor, followed by a data exchange phase where data are optionally exchanged between host and sensor. See section 8 Command List for a list of possible commands and the corresponding data exchanged. 

The byte order of all data exchanged is little-endian. 

# 7.3 Flash Write Commands

When sending a command that modifies flash memory (Set I2C Address, Set Comms Mode), the host needs to wait 30ms between transmitting the new value, and reading the response back from the sensor, to allow time for the sensor to commit the new value to memory. New flash variables only take effect after a device reset. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/b141eef6aa9ea6228b38fc1bd752cbf00c8ad31fff1dc2604801ffd027627022.jpg)


# 7.4 Interrupts

The INT pin is used during Active Mode to synchronize data transfer from the sensor to the host. When the sensor has acquired data, the INT pin is asserted to alert the host that new data are available. The process for retrieving data is different depending on the communication protocol. See section 7 Communication for more details. 

Interrupt line functionality will be expanded in future revisions. 

# 7.5 I2C Interface

I2C is an open drain communication system, so line capacitance must be minimized, and appropriate pull-up resistors must be present on both SCL and SDA for reliable operation. The pull up resistors should tie the SCL and SDA lines to VCC. 

When using the I2C interface, the sensor behaves as an I2C slave with clock stretching enabled. If the sensor requires more time to respond to commands, it will hold the SCL line low (for a maximum time of 40 milliseconds). 

The default sensor I2C address is 0x57. 

The Command Phase and Data Exchange Phase are performed as separate $\mathsf { I } ^ { 2 } \mathsf { C }$ transactions. 

# 7.5.1 Command Phase

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/c2eda7cc8b46c56d6da537ad0bbcf7e36d304103832e436a1d728115fe37f76c.jpg)


During the command phase, the sensor is selected by transferring the slave address (default 0x57) followed by a command byte. 

# 7.5.2 Data Exchange Phase

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/5dac6a7c0ed60df0178b1c1635de5015b8da3165987b60e90dd967ebe2a35ea2.jpg)


In the data exchange phase, the sensor waits for a read/write transaction of the appropriate number of bytes. After the host initiates a transaction by sending the slave address, the sensor may hold the SCL line low (clock stretching) to allow time for the sensor to be ready. 

During this phase, it is the responsibility of the host to ensure the correct number of bytes are exchanged. 

# 7.5.3 Active Mode Read

The recommended way to read data from a sensor running in Active mode is to monitor the interrupt pin (INT) to determine when new data have been acquired. The INT pin will be set HIGH when new data are available to be read. 

During Active mode, the host reads data from the sensor as per the Data Exchange Phase (with no Command Phase required). 

If the host attempts to read data faster than the ‘Active Frequency’, the sensor will hold the SCL line low (clock stretching) until the data are ready to be read. 

# 7.6 SPI Interface

This device uses SPI Mode 0 and supports SPI clock frequencies up to 3MHz. 

<table><tr><td>SPI Mode</td><td>CPOL</td><td>CPHA</td><td>SCK Idle State</td><td>Data Sampling</td></tr><tr><td>0</td><td>0</td><td>0</td><td>LOW</td><td>Data sampled on rising edge and shifted out on the falling edge</td></tr></table>

# 7.6.1 Command and Data Exchange

The Command Phase and Data Exchange Phase are performed in the same transaction, i.e. without deasserting. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/248d57e93ef205171dd221ba34f62fba8ae2dc42f2ac41fb7c9fa388362247a2.jpg)


To perform a successful SPI transaction, the host must: 

• Set ̅CS̅̅̅ LOW to select the sensor. 

• Send a single command byte (Command Phase). 

• Wait for a duration of at least tCD to allow the sensor to process and respond to the command. 

• Read/write 1 or more bytes, depending on the command (Data Exchange Phase). 

• Set ̅CS̅̅̅ HIGH to de-select the sensor. 

Following a transaction, the host must wait for a duration of at least $t _ { D C }$ before beginning another transaction. 


SPI Timing Parameters


<table><tr><td>Parameter</td><td>Symbol</td><td>Min</td><td>Max</td><td>Units</td></tr><tr><td>Command to Data Time</td><td><eq>t_{CD}</eq></td><td>250</td><td>-</td><td rowspan="2">μs</td></tr><tr><td>Data to Command Time</td><td><eq>t_{DC}</eq></td><td>10</td><td>-</td></tr></table>

# 7.6.2 Active Mode Read

The recommended way to read data from a sensor running in Active mode is to use the interrupt pin (INT) to synchronize transaction timing. 

To perform a successful SPI transaction in Active mode, the host must: 

• Wait for the INT pin to be set HIGH. This indicates the requested data has been acquired. 

• Set ̅CS̅̅̅ LOW to select the sensor. The sensor will move the data into the SPI write buffer. 

• Wait for the INT pin to be set LOW. This indicates the data is ready to be read. 

• Proceed with the SPI transaction as normal, shifting out the number of bytes determined by the Set Active Data command. 

• Set ̅CS̅̅̅ HIGH to de-select the sensor. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-05-16/10e299cc-aab0-4c84-9539-023e1e282ae3/f0eb4ddfbb8ea2d2fbc0a1ec9e8f75c1a36c80607984993f9ebe6f1bbc77143f.jpg)


If the interrupt pin is not used, it is the responsibility of the host application to ensure that the frequency of read requests is no quicker than the data frequency set with the Set Active Frequency command. In addition, the host must wait 3 µs after asserting before initiating an SPI data transfer. 


8 Command List


<table><tr><td>Command</td><td>Code (Hex)</td><td>Description</td><td>Write (bytes)</td><td>Read (bytes)</td></tr><tr><td>Reserved</td><td>0x00</td><td>Reserved.</td><td>-</td><td>-</td></tr><tr><td>NOP</td><td>0x01</td><td>No operation. Returns 0xAA.</td><td>-</td><td>1</td></tr><tr><td>Get Status</td><td>0x02</td><td>Retrieve device status.</td><td>-</td><td>1</td></tr><tr><td>Get Data</td><td>0x03</td><td>Read calibrated force and temperature data.</td><td>-</td><td>28</td></tr><tr><td>Get Temperature</td><td>0x04</td><td>Read device temperature.</td><td>-</td><td>4</td></tr><tr><td>Get Version</td><td>0x06</td><td>Read the device version.</td><td>-</td><td>32</td></tr><tr><td>Set Active Frequency</td><td>0x09</td><td>Set the acquisition frequency used when running in Active mode.</td><td>4</td><td>-</td></tr><tr><td>Get Active Frequency</td><td>0x0A</td><td>Read the current acquisition frequency.</td><td>-</td><td>4</td></tr><tr><td>Set Active Data</td><td>0x0B</td><td>Configure which data are to be acquired when running in Active mode.</td><td>4</td><td>-</td></tr><tr><td>Get Active Data</td><td>0x0C</td><td>Read which data are currently configured to be acquired in Active mode.</td><td>-</td><td>4</td></tr><tr><td>Enter Active</td><td>0x0D</td><td>Enter Active mode.</td><td>-</td><td>1</td></tr><tr><td>Bias Sensor</td><td>0x0F</td><td>Bias the sensor.</td><td>-</td><td>1</td></tr><tr><td>Set I2C Address</td><td>0x10</td><td>Set a new I2C Address for this device. The new address will take affect after a reset.</td><td>1^</td><td>1</td></tr><tr><td>Who Am I</td><td>0x11</td><td>Retrieve hardware ID.</td><td>-</td><td>32#</td></tr><tr><td>Set Comms Mode</td><td>0x13</td><td>Set the communication interface for this device (I2C/SPI).</td><td>1^</td><td>1</td></tr><tr><td>Other Commands</td><td></td><td>Reserved. Do not use</td><td>Reserved</td><td>Reserved</td></tr></table>


* All values are little endian. 



^ Flash write commands should be followed by a 100ms delay. 



# Null terminated string. 


# 9 Command Descriptions

# 9.1 NOP

Command: 0x01 

Rx size: 1 byte 

This command returns 0xAA. This command can be used to verify communication with the device. 

# 9.2 Get Status

Command: 0x02 

Rx size: 1 byte 

Reads the error status from the device. The status is a single unsigned byte: 

<table><tr><td>Status</td><td>Code (Hex)</td><td>Description</td></tr><tr><td>Out Of Range</td><td>0x01</td><td>Attempt to access an out-of-range memory address.</td></tr><tr><td>Memory Allocation Error</td><td>0x02</td><td>Memory allocation failed. Insufficient internal memory.</td></tr><tr><td>OK</td><td>0xAA</td><td>No error. Sensor is operating as expected.</td></tr><tr><td>Bad Calibration</td><td>0xFD</td><td>There is a problem with the calibration on the device.</td></tr><tr><td>Error</td><td>0xFE</td><td>Generic error.</td></tr><tr><td>Status Unknown</td><td>0xFF</td><td>Device status is unknown.</td></tr></table>

# 9.3 Get Data

Command: 0x03 

Rx size: 28 bytes 

The sensor will collect and process 3D force and temperature data. All processed data are transmit as 32-bit floating-point values. Data are sent in the following order: 

<table><tr><td>Starting Byte</td><td>Description</td></tr><tr><td>0</td><td>Force applied in the X axis</td></tr><tr><td>4</td><td>Force applied in the Y axis</td></tr><tr><td>8</td><td>Force applied in the Z axis</td></tr><tr><td>12 – 23</td><td>Reserved</td></tr><tr><td>24</td><td>On-board temperature</td></tr></table>

Note: After receiving the Get Data command, the sensor takes approximately 300μs to sample 3D force and temperature data. The SCL line will be held low by the sensor during this time. 

# 9.4 Get Temperature

Command: 0x04 

Rx size: 4 bytes 

The sensor will sample and transmit the on-board temperature as a single 32-bit floating-point value. 

# 9.5 Get Version

Command: 0x06 

Rx size: 32 bytes 

The sensor transmits its firmware version as a 32-byte null-terminated string. 

# 9.6 Set Active Frequency

Command: 0x09 

Tx size: 4 bytes 

The command is used to define the data processing rate in Active mode. By default, the sensor will collect and process pillar data at 1000 Hz. The minimum active frequency is 25 Hz. 

The sensor expects to receive a 32-bit unsigned integer to set the active frequency. 

# 9.7 Get Active Frequency

Command: 0xA 

Rx size: 4 bytes 

The sensor transmits the current Active frequency as a 32-bit unsigned integer. 

# 9.8 Set Active Data

Command: 0xB 

Tx size: 4 bytes 

This command is used to set which data are to be processed and transmitted during the Active state. The sensor expects a 32-bit bitfield in the following format. All values are set to 0 after a reset. 


Active Data Bitfield


<table><tr><td>Bit number</td><td>Data</td></tr><tr><td>31-16</td><td>Reserved</td></tr><tr><td>11</td><td>Force applied in the X axis</td></tr><tr><td>10</td><td>Force applied in the Y axis</td></tr><tr><td>9</td><td>Force applied in the Z axis</td></tr><tr><td>8-6</td><td>Reserved *</td></tr><tr><td>5</td><td>On-board temperature</td></tr><tr><td>4-0</td><td>Reserved *</td></tr></table>


* Setting Reserved fields can cause erroneous data and communication issues. 


# 9.9 Get Active Data

Command: 0x0C 

Rx size: 4 bytes 

The sensor will transmit the active data bitfield. See ‘Set Active Data’ for details regarding the active data bitfield. The data are transmitted as a 32-bit unsigned integer. 

# 9.10 Enter Active

Command: 0x0D 

Rx size: 1 byte 

This command is used to place the sensor in Active mode. The sensor transmits a 1-byte unsigned integer to indicate if the transition to Active mode was successful: 

<table><tr><td>Response</td><td>Meaning</td></tr><tr><td>0xAA</td><td>Enter Active mode was successful</td></tr><tr><td>0xFE</td><td>Enter Active mode failed. Check active data bitfield.</td></tr></table>

The sensor enters active mode after the one-byte response is read. 

After entering Active mode, the sensor continuously acquires the force and temperature data that were requested by ‘Set Active Data’ at the ‘Active Frequency’. The host can read the corresponding number of bytes to retrieve the latest data. All force and temperature values are 32-bit floating-point values. 

When in Active mode, the host should only read from the sensor. Active mode will exit automatically and return to Idle mode when any command is issued. 

The host should read 4 bytes for every valid bit in the Active Data Bitfield. Data are transferred in the order listed in this bitfield. See Set Active Data for more details. 

The host can read at any desired rate, but will only read the latest sampled data. There is no on-board buffering; unread data are discarded. 

# 9.11 Bias Sensor

Command: 0x0F 

Rx size: 1 byte 

This command is used to bias the sensor. The sensor collects 3D force data to calculate bias constants. 

Biasing the sensor is akin to taring a weighing scale, it sets a baseline from which to calculate readings. This command should be run with no force applied to the pillars to calculate accurate bias constants. This command must be run at least once to receive valid force data. 

The sensor sends a 1 byte response indicating if biasing was successful. A response of 0xAA indicates success. 

# 9.12 Set I2C Address

Command: 0x10 

Tx size: 1 byte 

Rx size: 1 byte 

Modifies flash memory ^ 

This command is used to permanently change the I2C address for the device. The data phase for this command has two transactions. The first is a Tx phase with a size of 1 byte where the sensor expects a 7-bit I2C address (LSB at bit 0). An Rx phase follows, with a read size of 1 byte where the sensor transmits the new I2C address as it was received/stored on-board. 

A reset is required for the new address to take effect. 

^ See section 7.3 Flash Write Commands for timing requirements for this command. 

# 9.13 Who Am I

Command: 0x11 

Rx size: 32 bytes 

This command is used to read the sensor’s hardware details. The sensor transmits 32 bytes in the form of a null terminated string. All 32 bytes must be read from the sensor. 

# 9.14 Set Comms Mode

Command: 0x13 

Tx size: 1 byte 

Rx size: 1 byte 

Modifies flash memory ^ 

This command is used to permanently change the communication interface for the device. The data phase for this command has two transactions. The first is a Tx phase where the host sends the desired communication interface (I2C = 0x00, SPI = 0x01). An Rx phase follows, with a read size of 1 byte where the sensor transmits the new communication interface as it was received/stored on-board. 

<table><tr><td>Communication Interface</td><td>Tx phase data byte</td></tr><tr><td><eq>I^{2}C</eq></td><td>0x00</td></tr><tr><td>SPI</td><td>0x01</td></tr></table>

A reset is required for the new communication interface to take effect. 

^ See section 7.3 Flash Write Commands for timing requirements for this command. 

The communication interface may also be changed using Interface Bootstrapping. 

# 10 Important Notes

# 10.1 Communication Check

The ‘NOP’ command can be used to check communication with the sensor and ensure the sensor is transmitting as expected. The ‘Set Active Frequency’ and ‘Get Active Frequency’ commands can be used to ensure that data are being transmitted to the sensor at the rate expected. 

# 10.2 Address Collision

To use multiple sensors on the same I2C bus, the ‘Set I2C Address’ command can be used to assign new addresses to sensors. Other sensors may be held in reset to avoid collisions during I2C address assignment. 

# 10.3 Data Exchange Phase

The correct number of bytes must be exchanged in each phase, otherwise the sensor may enter a nonresponsive state. This can be seen when the response to any command is all 1’s or the sensor does not respond at all. Reset the sensor to restore communication. 

# 11 Revision History

<table><tr><td>Date</td><td>Revision</td><td>Changes</td></tr><tr><td>24 May 2024</td><td>1</td><td>Described changes available from firmware version 1.1.0Added SPI communication interface;Added SPI timing diagrams;Updated Pinout;Revised section 7 Communication;Expanded interrupt description;Added command Set Comms Mode to Command List;Flash write commands now require only 30ms between writing command and reading response (previously 100ms);The ‘Bias’ command now includes a data exchange phase. Updated diagrams and description to indicate this;‘OK’ status code changed from 0x00 to 0xAA</td></tr></table>

# 12 Resources

[1] C3DFBS library for a host micro-controller: https://github.com/contactile/c3dfbs 