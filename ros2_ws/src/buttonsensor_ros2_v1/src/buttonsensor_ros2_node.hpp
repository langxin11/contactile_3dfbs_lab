#ifndef BUTTONSENSOR_ROS2_V1_NODE_HPP_
#define BUTTONSENSOR_ROS2_V1_NODE_HPP_

#include <stdio.h>
#include <memory>
#include <vector>
#include <string>
#include <chrono>


#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/header.hpp"

// Messages
#include "sensor_interfaces/msg/button_sensor_state.hpp"

// Services
#include "sensor_interfaces/srv/bias_request.hpp"

#ifndef PTSDKCONSTANTS_H
#include <PTSDKConstants.h>
#endif
// Workaround for vendor SDK: PTSDKListener.h defines BYTE as byte and also
// imports std::byte via "using namespace std", which is ambiguous under ROS2.
#ifdef __unix__
#define byte unsigned char
#endif
#ifndef PTSDKLISTENER_H
#include <PTSDKListener.h>
#endif
#ifdef __unix__
#undef byte
#endif
#ifndef PTSDKSENSOR_H
#include <PTSDKSensor.h>
#endif

class ButtonSensorNode : public rclcpp::Node {
public:
    // Constructor
    ButtonSensorNode(const rclcpp::NodeOptions & options);

    // Destructor
    ~ButtonSensorNode() {
        // Stop listening for and processing data and disconnect from the COM port
        listener_.stopListeningAndDisconnect();
    }

    // Update sensor data and publish
    void updateData();

    // Get the sampling rate
    int getSamplingRate(){ return sampling_rate_; };

private:
    int hub_id_;
    int n_sensors_;
    std::string port_;
    int baud_rate_;
    int parity_;
    int byte_size_;
    int sampling_rate_;

    PTSDKListener listener_;
    std::vector<std::unique_ptr<PTSDKSensor> > sensors_;

    // Sensor publishers
    std::vector<rclcpp::Publisher<sensor_interfaces::msg::ButtonSensorState>::SharedPtr> sensor_pubs_;

    // Services
    rclcpp::Service<sensor_interfaces::srv::BiasRequest>::SharedPtr send_bias_request_srv_;

    // Service callback functions
    bool sendBiasRequestSrvCallback([[maybe_unused]] const std::shared_ptr<sensor_interfaces::srv::BiasRequest::Request> request,
                    std::shared_ptr<sensor_interfaces::srv::BiasRequest::Response> response);

};

#endif // BUTTONSENSOR_ROS2_V1_NODE_H_
