import logging
import unittest
from time import sleep
import time
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
        pass

    def tearDown(self):
        pass

    def testConnectAndDisconnect(self):
        """Test que verifica la conexión y desconexión del cliente MQTT"""
        logging.info("Running testConnectAndDisconnect...")

        # Conectar al broker
        connected = self.mcc.connectClient()
        self.assertTrue(connected, "El cliente MQTT debería conectarse exitosamente.")
        sleep(2)

        # Verificar que la conexión ha sido realizada correctamente revisando el estado del cliente
        self.assertTrue(self.mcc.mqttClient.is_connected(), "El cliente MQTT debería estar conectado.")

        # Desconectar del broker
        disconnected = self.mcc.disconnectClient()
        self.assertTrue(disconnected, "El cliente MQTT debería desconectarse exitosamente.")
        sleep(2)

        # Verificar que la desconexión ha sido realizada correctamente
        self.assertFalse(self.mcc.mqttClient.is_connected(), "El cliente MQTT debería estar desconectado.")

    def testServerPing(self):
        # Conectar al broker MQTT
        isConnected = self.mcc.connectClient()
        assert isConnected, "Connection to MQTT broker failed"

        # Mantener la conexión abierta durante el tiempo suficiente para generar los paquetes PINGREQ y PINGRESP
        time.sleep(6)  # Ajusta el tiempo para que la conexión permanezca activa (más que el Keep-Alive)

        # El paquete PINGRESP debe ser recibido automáticamente por el broker
        logging.info("Ping test completed, PINGREQ and PINGRESP exchanged.")

        # Desconectar del broker
        self.mcc.disconnectClient()

    def testPubSub(self):
        #Test que verifica que la publicación y suscripción funcionan correctamente con QoS 1 y QoS 2
        logging.info("Running testPubSub...")

        # Conectar al broker
        connected = self.mcc.connectClient()
        self.assertTrue(connected, "El cliente MQTT debería conectarse exitosamente.")

        # Suscribirse al tema con QoS 1
        subscribed = self.mcc.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos=1)
        self.assertTrue(subscribed, "El cliente MQTT debería suscribirse exitosamente al tema con QoS 1.")
        sleep(2)  # Espera para asegurar que la suscripción ha sido procesada

        # Publicar un mensaje con QoS 1
        message = ActuatorData(typeID=1, name="Actuator1")

        published = self.mcc.publishMessage(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,DataUtil().actuatorDataToJson(message), qos=1)

        self.assertTrue(published, "El cliente MQTT debería publicar el mensaje con QoS 1.")
        sleep(2)  # Espera para asegurar que el mensaje ha sido entregado

        # Suscribirse al tema con QoS 2
        subscribed = self.mcc.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos=2)
        self.assertTrue(subscribed, "El cliente MQTT debería suscribirse exitosamente al tema con QoS 2.")
        sleep(2)  # Espera para asegurar que la suscripción ha sido procesada

        # Publicar un mensaje con QoS 2
        published = self.mcc.publishMessage(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, DataUtil().actuatorDataToJson(message), qos=2)
        self.assertTrue(published, "El cliente MQTT debería publicar el mensaje con QoS 2.")
        sleep(2)  # Espera para asegurar que el mensaje ha sido entregado

        # Desconectar después del test
        self.mcc.disconnectClient()

# Ejecutar los tests
if __name__ == '__main__':
    unittest.main()