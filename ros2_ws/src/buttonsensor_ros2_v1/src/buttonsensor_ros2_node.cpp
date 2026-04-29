#include "buttonsensor_ros2_node.hpp"

ButtonSensorNode::ButtonSensorNode([[maybe_unused]] const rclcpp::NodeOptions &options) : Node("buttonsensor_ros2_v1_node"), listener_(true) {
    RCLCPP_INFO(this->get_logger(), "Loading parameters...\n");
    hub_id_ = this->declare_parameter("hub_id", 0);
    RCLCPP_INFO(this->get_logger(), "Hub id: %d", hub_id_);

    n_sensors_ = this->declare_parameter("n_sensors", 0);
    if (n_sensors_ > MAX_NSENSOR || n_sensors_ < 1) {
        RCLCPP_ERROR(this->get_logger(), "\033[91mInvalid number of sensors!  %d selected (must be no more than %d)\033[0m", n_sensors_, MAX_NSENSOR);
    } else {
        RCLCPP_INFO(this->get_logger(), "\033[92mUsing %d sensor/s\033[0m", n_sensors_);
    }

    port_ = this->declare_parameter("com_port", std::string(""));
    RCLCPP_INFO(this->get_logger(), "Reading from serial COM port: %s", port_.c_str());

    baud_rate_ = this->declare_parameter("baud_rate", 0);
    RCLCPP_INFO(this->get_logger(), "Baud rate: %d Hz", baud_rate_);

    parity_ = this->declare_parameter("parity", 0);
    RCLCPP_INFO(this->get_logger(), "Parity set to: %d (0=PARITY_NONE, 1=PARITY_ODD, 2=PARITY_EVEN)", parity_);

    byte_size_ = this->declare_parameter("byte_size", 0);
    RCLCPP_INFO(this->get_logger(), "Byte size: %d bits", byte_size_);

    sampling_rate_ = this->declare_parameter("sampling_rate", 0);
    RCLCPP_INFO(this->get_logger(), "Sampling rate: %d Hz", sampling_rate_);

    RCLCPP_INFO(this->get_logger(), "Loaded parameters.\n");

    // Resize sensors_ to the required size
    sensors_.resize(n_sensors_);

    // Create sensors and add to listener
    RCLCPP_INFO(this->get_logger(), "Creating sensors...\n");

    for (size_t sensor_id = 0; sensor_id < static_cast<size_t>(n_sensors_); sensor_id++) {
        RCLCPP_INFO(this->get_logger(), "Creating sensor %zu...", sensor_id);
        auto sensor = std::make_unique<PTSDKSensor>();
        RCLCPP_INFO(this->get_logger(), "Adding sensor %zu to listener...", sensor_id);
        listener_.addSensor(sensor.get());
        RCLCPP_INFO(this->get_logger(), "Added sensor %zu to listener!\n", sensor_id);
        sensors_[sensor_id] = std::move(sensor);

        // Setup publisher for sensor
        std::string topic = "/hub_" + std::to_string(hub_id_) + "/sensor_" + std::to_string(sensor_id);
        sensor_pubs_.push_back(this->create_publisher<sensor_interfaces::msg::ButtonSensorState>(topic, sampling_rate_));
    }

    // Start services
	RCLCPP_INFO(this->get_logger(), "Starting services...");
	std::string service_name = "/hub_" + std::to_string(hub_id_) + "/send_bias_request";
	send_bias_request_srv_ = this->create_service<sensor_interfaces::srv::BiasRequest>(service_name, 
		[this]([[maybe_unused]] const std::shared_ptr<sensor_interfaces::srv::BiasRequest::Request> request, 
			std::shared_ptr<sensor_interfaces::srv::BiasRequest::Response> response) {
			return sendBiasRequestSrvCallback(request, response);
		});
	RCLCPP_INFO(this->get_logger(), "Started %s service", service_name.c_str());

    // Start listener
    RCLCPP_INFO(this->get_logger(), "Connecting to %s port...", port_.c_str());
    if (listener_.connect(port_.c_str(), baud_rate_, parity_, char(byte_size_))) {
        RCLCPP_FATAL(this->get_logger(), "\033[91mFailed to connect to port: %s\033[0m", port_.c_str());
        rclcpp::shutdown();
    } else {
        RCLCPP_INFO(this->get_logger(), "\033[92mConnected to port: %s\033[0m", port_.c_str());
    }

	// // Set sampling rate
	// RCLCPP_INFO(this->get_logger(), "Setting sampling rate to %u...", sampling_rate_);
	// if (!listener_.setSamplingRate(sampling_rate_)) {
	// 	RCLCPP_WARN(this->get_logger(), "\033[91mFailed to set sampling rate to: %u\033[0m", sampling_rate_);
	// } else {
	// 	RCLCPP_INFO(this->get_logger(), "\033[92mSampling rate set to %u\033[0m", sampling_rate_);
	// }
}

void ButtonSensorNode::updateData() {
    if (n_sensors_ == 0) {
        return;
    }

    // Read next sample from COM port
    listener_.readNextSample();

    for (size_t sensor_id = 0; sensor_id < sensors_.size(); sensor_id++) {
        sensor_interfaces::msg::ButtonSensorState ss_msg;

        auto time = now();

        long timestamp_us = sensors_[sensor_id]->getTimestamp_us();
        ss_msg.tus = timestamp_us;

        double globalForce[NDIM];
        // Read global forces
        sensors_[sensor_id]->getGlobalForce(globalForce);
        ss_msg.gfx = static_cast<float>(globalForce[X_IND]);
        ss_msg.gfy = static_cast<float>(globalForce[Y_IND]);
        ss_msg.gfz = static_cast<float>(globalForce[Z_IND]);

        // Publish ButtonSensorState message
        sensor_pubs_[sensor_id]->publish(ss_msg);
    }
}

bool ButtonSensorNode::sendBiasRequestSrvCallback([[maybe_unused]] const std::shared_ptr<sensor_interfaces::srv::BiasRequest::Request> req,
                     std::shared_ptr<sensor_interfaces::srv::BiasRequest::Response> resp) {
	RCLCPP_INFO(this->get_logger(), "sendBiasRequest callback");
	resp->result = listener_.sendBiasRequest();
	std::this_thread::sleep_for(std::chrono::milliseconds(100)); // wait
	return resp->result;
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ButtonSensorNode>(rclcpp::NodeOptions());

    rclcpp::Rate loop_rate(node->getSamplingRate());

    while (rclcpp::ok()) {
        rclcpp::spin_some(node);
        loop_rate.sleep();
        node->updateData(); // Update sensor data and publish
    }

    rclcpp::shutdown();

    return 0;
}
