import logging
import unittest
from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil


class MqttClientControlPacketTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Executing the MqttClientControlPacketTest class...")

        cls.cfg = ConfigUtil()

        # NOTE: Be sure to use a DIFFERENT clientID than that which is used
        # for your CDA when running separately from this test
        #
        # The clientID shown below is an example only - please use your own
        # unique value for this test
        cls.mcc = MqttClientConnector(clientID="MyTestMqttClient")

    def setUp(self):
        """
        Setup the test environment, ensuring a clean state for each test.
        """
        self.mcc.connectClient()

    def tearDown(self):
        """
        Cleanup after each test.
        """
        self.mcc.disconnectClient()

    def testConnectAndDisconnect(self):
        """
        Test the connection and disconnection functionality of the MQTT client.
        Ensure that the client can connect to and disconnect from the broker.
        """
        logging.info("Testing connection to MQTT broker...")
        self.assertTrue(self.mcc.connectClient())

        logging.info("Testing disconnection from MQTT broker...")
        if self.mcc.mqttClient.is_connected():
            self.assertTrue(self.mcc.disconnectClient())
        else:
            logging.warning("MQTT client was not connected, skipping disconnect test.")

    def testServerPing(self):
        """
        Test the PING functionality to ensure the MQTT client is still connected.
        """
        logging.info("Testing PING to MQTT broker...")


        ping_result = self.mcc.ping()

        self.assertTrue(ping_result, "Failed to send PING message to broker")


    def testPubSub(self):
        """
        Test the publish and subscribe functionality with QoS 1 and QoS 2.
        Ensure the control packets are generated for each QoS level.
        """
        topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE
        message_qos1 = "Test message for QoS 1"
        message_qos2 = "Test message for QoS 2"

        # Publish QoS 1
        logging.info("Testing message publish with QoS 1...")
        publish_result_qos1 = self.mcc.publishMessage(topic, message_qos1, qos=1)
        self.assertTrue(publish_result_qos1, "Failed to publish message with QoS 1")

        # Publish QoS 2
        logging.info("Testing message publish with QoS 2...")
        publish_result_qos2 = self.mcc.publishMessage(topic, message_qos2, qos=2)
        self.assertTrue(publish_result_qos2, "Failed to publish message with QoS 2")

        # Subscribe QoS 1
        logging.info("Testing subscribe with QoS 1...")
        subscribe_result_qos1 = self.mcc.subscribeToTopic(topic, qos=1)
        self.assertTrue(subscribe_result_qos1, "Failed to subscribe to topic with QoS 1")

        # Subscribe QoS 2
        logging.info("Testing subscribe with QoS 2...")
        subscribe_result_qos2 = self.mcc.subscribeToTopic(topic, qos=2)
        self.assertTrue(subscribe_result_qos2, "Failed to subscribe to topic with QoS 2")

        sleep(2)

        logging.info("Testing unsubscribe functionality...")
        unsubscribe_result = self.mcc.unsubscribeFromTopic(topic)
        self.assertTrue(unsubscribe_result, "Failed to unsubscribe from topic")
