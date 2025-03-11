#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

from json import JSONEncoder
import json
import logging

from decimal import Decimal
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class DataUtil():
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, encodeToUtf8=False):
		self.encodeToUtf8 = encodeToUtf8
		logging.info("Created DataUtil instance.")


	def actuatorDataToJson(self, data: ActuatorData = None, useDecForFloat: bool = False):
		if data:
			return json.dumps(data, indent=4, cls=JsonDataEncoder)
		return None

	def sensorDataToJson(self, data: SensorData = None, useDecForFloat: bool = False):
		if data:
			return json.dumps(data, indent=4, cls=JsonDataEncoder)
		return None

	def systemPerformanceDataToJson(self, data: SystemPerformanceData = None, useDecForFloat: bool = False):
		if data:
			return json.dumps(data, indent=4, cls=JsonDataEncoder)
		return None

	def _jsonToObject(self, jsonData: str, objType):
		if jsonData:
			jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
			jsonStruct = json.loads(jsonData)

			obj = objType()
			varStruct = vars(obj)

			for key in jsonStruct:
				if key in varStruct:
					setattr(obj, key, jsonStruct[key])

			return obj
		return None

	def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False):
		return self._jsonToObject(jsonData, ActuatorData)

	def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False):
		return self._jsonToObject(jsonData, SensorData)

	def jsonToSystemPerformanceData(self, jsonData: str = None, useDecForFloat: bool = False):
		return self._jsonToObject(jsonData, SystemPerformanceData)


class JsonDataEncoder(JSONEncoder):
	"""
    Convenience class to facilitate JSON encoding of an object that
    can be converted to a dict.
    """

	def default(self, o):
		return o.__dict__