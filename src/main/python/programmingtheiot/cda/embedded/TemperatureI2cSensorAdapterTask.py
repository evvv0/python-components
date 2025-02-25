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


class TemperatureI2cSensorAdapterTask(BaseSensorSimTask):
	def __init__(self):
		super(TemperatureI2cSensorAdapterTask, self).__init__(typeID=SensorData.TEMPERATURE_SENSOR_TYPE,
															  minVal=SensorDataGenerator.LOW_NORMAL_ENV_TEMP,
															  maxVal=SensorDataGenerator.HI_NORMAL_ENV_TEMP)
		self.sensorType = SensorData.TEMPERATURE_SENSOR_TYPE
		self.tempAddr = 0x61  # Dirección del sensor de temperatura (Ejemplo)
		self.i2cBus = smbus.SMBus(1)
		self.i2cBus.write_byte_data(self.tempAddr, 0, 0)

	def generateTelemetry(self) -> SensorData:
		try:
			tempRaw = self.i2cBus.read_word_data(self.tempAddr, 0x03)
			temp = (tempRaw / 100.0)  # Conversión a grados Celsius
			self.sensorData = SensorData(sensorType=self.sensorType, value=temp)
			return self.sensorData
		except Exception as e:
			logging.error("Error al generar telemetría de temperatura: %s", e)
			return None

	def getTelemetryValue(self) -> float:
		if self.sensorData:
			return self.sensorData.value
		return 0.0