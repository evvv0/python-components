#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging

from programmingtheiot.data.SensorData import SensorData
import smbus

class PressureI2cSensorAdapterTask(BaseSensorSimTask):
	def __init__(self):
		super(PressureI2cSensorAdapterTask, self).__init__(typeID=SensorData.PRESSURE_SENSOR_TYPE,
														   minVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE,
														   maxVal=SensorDataGenerator.HI_NORMAL_ENV_PRESSURE)
		self.sensorType = SensorData.PRESSURE_SENSOR_TYPE
		self.pressureAddr = 0x60  # Dirección del sensor de presión (Ejemplo)
		self.i2cBus = smbus.SMBus(1)
		self.i2cBus.write_byte_data(self.pressureAddr, 0, 0)

	def generateTelemetry(self) -> SensorData:
		try:
			pressureRaw = self.i2cBus.read_word_data(self.pressureAddr, 0x02)
			pressure = (pressureRaw / 10.0)  # Conversión de datos a presión
			self.sensorData = SensorData(sensorType=self.sensorType, value=pressure)
			return self.sensorData
		except Exception as e:
			logging.error("Error al generar telemetría de presión: %s", e)
			return None

	def getTelemetryValue(self) -> float:
		if self.sensorData:
			return self.sensorData.value
		return 0.0