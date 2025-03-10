#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import smbus
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator


class HumidityI2cSensorAdapterTask(BaseSensorSimTask):
	"""
    Clase adaptadora para leer datos del sensor de humedad a través de I2C.
    """

	def __init__(self):
		# Inicializa la clase base con los valores de sensor
		super(HumidityI2cSensorAdapterTask, self).__init__(typeID=SensorData.HUMIDITY_SENSOR_TYPE,
														   minVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY,
														   maxVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY)

		self.sensorType = SensorData.HUMIDITY_SENSOR_TYPE

		# Dirección I2C para el sensor de humedad
		self.humidAddr = 0x5F  # Dirección del sensor de humedad (por ejemplo, para SenseHAT)

		# Inicializa el bus I2C en el Raspberry Pi (sólo bus 1)
		self.i2cBus = smbus.SMBus(1)
		self.i2cBus.write_byte_data(self.humidAddr, 0, 0)

	def generateTelemetry(self) -> SensorData:
		"""
        Lee los valores del sensor de humedad a través de I2C y genera los datos del sensor.
        """
		try:
			# Lee los datos del sensor (esto puede variar según el sensor)
			humidityRaw = self.i2cBus.read_word_data(self.humidAddr, 0x01)

			# Convierte los datos crudos en un valor de humedad (esto depende de tu sensor)
			humidity = (humidityRaw / 100.0)  # Ajuste para convertir a porcentaje de humedad (ejemplo)

			# Actualiza el sensor con los datos generados
			self.sensorData = SensorData(sensorType=self.sensorType, value=humidity)

			# Devuelve el objeto SensorData
			return self.sensorData
		except Exception as e:
			logging.error("Error al generar telemetría de humedad: %s", e)
			return None

	def getTelemetryValue(self) -> float:
		"""
        Obtiene el valor de telemetría de humedad como un número flotante.
        """
		if self.sensorData:
			return self.sensorData.value
		else:
			return 0.0  # Retorna un valor por defecto si no hay datos


