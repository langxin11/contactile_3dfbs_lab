// USER_APP_EXAMPLE.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include <stdio.h>
#ifdef _WIN32
#include <tchar.h>
#endif

#ifndef PTSDKCONSTANTS_H
#include "PTSDKConstants.h"
#endif
#ifndef PTSDKLISTENER_H
#include "PTSDKListener.h"
#endif
#ifndef PTSDKSENSOR_H
#include "PTSDKSensor.h"
#endif

#ifndef _WIN32
#include <ctime>
#include <chrono>
#include <thread>
#endif

#ifdef _WIN32
int _tmain(int argc, _TCHAR* argv[])
#else
int main()
#endif
{
	int example;
	//example = 1;
	example = 2;

	bool isLogging;
	isLogging = true;
	//isLogging = false;

	/* Initialise a PTSDKSensor object for four sensors */
	PTSDKSensor sen0 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN0 port of the comms hub
	PTSDKSensor sen1 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN0 port of the comms hub
	PTSDKSensor sen2 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen3 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen4 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen5 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen6 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen7 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen8 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub
	PTSDKSensor sen9 = PTSDKSensor(); // The sensor connected to the  ? port of the adaptor connected to the SEN1 port of the comms hub


	/* Initialise the PTSDKListener object */
	PTSDKListener listener = PTSDKListener(isLogging);

	/* Add all four sensors to the listener */
	listener.addSensor(&sen0);
	listener.addSensor(&sen1);
	listener.addSensor(&sen2);
	listener.addSensor(&sen3);
	listener.addSensor(&sen4);
	listener.addSensor(&sen5);
	listener.addSensor(&sen6);
	listener.addSensor(&sen7);
	listener.addSensor(&sen8);
	listener.addSensor(&sen9);

	/* Initialise connection parameters */
#ifdef _WIN32
	char port[] = "\\\\.\\COM5"; 	// The name of the COM port to connect with
#else
	char port[] = "/dev/ttyACM0";
#endif
	// The additional ‘\’ characters are required
	int rate = 11520;//9600; 			// The rate of the serial connection
	int parity = 0; 				// 0=PARITY_NONE, 1=PARITY_ODD, 2=PARITY_EVEN
	char byteSize = 8; 				// The number of bits in a byte
	int logFileRate = LOG_RATE_1000;// The rate (Hz) to write to the log file: LOG_RATE_1000 or LOG_RATE_500 or LOG_RATE_100


	/*
	 * EXAMPLE 1: Multi-threaded
	 */
	if (example == 1) {
		/* Connect to the serial port and start listening for and processing data in a separate thread */
		int err = listener.connectAndStartListening(port, rate, parity, byteSize, logFileRate);

		std::this_thread::sleep_for(std::chrono::milliseconds(100));

		/* Perform bias */
		if(listener.sendBiasRequest()){
			printf("Successfully sent bias request.\n");
		}else{
			printf("FAILED to send bias request.\n");
			return -1;
		}

		/* Print sample once every second for 10 seconds */
		for (int i = 0; i < 10; i++) {
#ifdef _WIN32
			Sleep(100);
#else
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
#endif
			double globalForce[NDIM];
			sen0.getGlobalForce(globalForce);
			for (int dInd = 0; dInd < NDIM; dInd++) {
				printf("S0: global F%d = %.3f\n", dInd, globalForce[dInd]);
			}
			printf("\n");
		}

		/* Stop listening and disconnect from the serial port */
		listener.stopListeningAndDisconnect();
		return 0;
	}


	/*
	 * EXAMPLE 2: 
	 */

	if (example == 2) {
		/* Connect to serial port */
		int err = listener.connect(port, rate, parity, byteSize);

		/* Check if the connection was successful */
		if (err) {
			printf("Could not connect to %s\n", port);
			return -1;
		}
		else {
			printf("Connected successfully to %s\n", port);
		}


		std::this_thread::sleep_for(std::chrono::milliseconds(100));

		/* Perform bias */
		if(listener.sendBiasRequest()){
			printf("Successfully sent bias request.\n");
		}else{
			printf("FAILED to send bias request.\n");
			return -1;
		}


		/* Read samples and do something */
		while (true) {
			bool res = listener.readNextSample();
			if (res) {
				// Do something
				printf("main(): Read sample SUCCESSFULLY:\n");
				double globalForce[NDIM];
				sen0.getGlobalForce(globalForce);
				for (int dInd = 0; dInd < NDIM; dInd++) {
					printf("S0: global F%d = %.3f\n", dInd, globalForce[dInd]);
				}
				printf("\n");

			}
			else {
				printf("main(): Read sample FAILED!\n");
			}
		}

		listener.disconnect();
		return 0;
	}

}

