#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import socket
import traceback

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient
from programmingtheiot.data.DataUtil import DataUtil

import asyncio

from aiocoap import*

class CoapClientConnector(IRequestResponseClient):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, dataMsgListener: IDataMessageListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		self.coapClient = None

		self.observeRequests = {}

		self.host = self.config.getProperty(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.HOST_KEY,
			ConfigConst.DEFAULT_HOST
		)
		self.port = self.config.getInteger(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.PORT_KEY,
			ConfigConst.DEFAULT_COAP_PORT
		)
		self.uriPath = "coap://" + self.host + ":" + str(self.port) + "/"

		logging.info('\tHost:Port: %s:%s', self.host, str(self.port))

		self.includeDebugLogDetail = True

		try:
			tmpHost = socket.gethostbyname(self.host)

			if tmpHost:
				self.host = tmpHost
				self._initClient()
			else:
				logging.error("Can't resolve host: " + self.host)

		except socket.gaierror:
			logging.info("Failed to resolve host: " + self.host)
	
	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		logging.info("sendDiscoveryRequest called.")
		return False

	def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			# Construir URI correctamente
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath  # Incluye host:puerto
			else:
				resourcePath = name  # ya es una URI completa

			logging.info("Issuing Async DELETE to path: " + resourcePath)

			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleDeleteRequest(
						resourcePath=resourcePath,
						enableCON=enableCON
					)
				)
			except Exception as e:
				logging.warning("Error during Async DELETE execution.")
				traceback.print_exception(type(e), e, e.__traceback__)
		else:
			logging.warning("Can't issue Async DELETE - no path or path list provided.")
	async def _handleDeleteRequest(self, resourcePath: str = None, enableCON: bool = False):
		try:
			msgType = NON
			if enableCON:
				msgType = CON

			msg = Message(mtype=msgType, code=Code.DELETE, uri=resourcePath)
			req = self.coapClient.request(msg)

			responseData = await req.response
			self._onDeleteResponse(responseData)

		except Exception as e:
			logging.warning("Failed to process DELETE request for path: " + str(resourcePath))
			traceback.print_exception(type(e), e, e.__traceback__)

	def _onDeleteResponse(self, response):
		if not response:
			logging.warning('DELETE response invalid. Ignoring.')
			return

		try:
			responseText = response.payload.decode('utf-8')
			logging.info('DELETE response received: %s', responseText)
		except Exception as e:
			logging.warning('Failed to decode DELETE response.')
			traceback.print_exception(type(e), e, e.__traceback__)

	def sendGetRequest(	self, resource: ResourceNameEnum = None, name: str = None,	enableCON: bool = False,timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			# Construir la URI completa correctamente
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath  # uriPath ya incluye host:port
			else:
				resourcePath = name  # ya es una URI completa, como 'coap://localhost:5683/.well-known/core'

			logging.info("Issuing Async GET to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handleGetRequest(resourcePath=resourcePath, enableCON=enableCON)
			)
		else:
			logging.warning("Can't issue Async GET - no path or path list provided.")

	async def _handleGetRequest(self, resourcePath: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			msg = Message(mtype=msgType, code=Code.GET, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onGetResponse(responseData)

		except Exception as e:
			logging.warning("Failed to process GET request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)


	def _onGetResponse(self, response):
		if not response:
			logging.warning('Async GET response invalid. Ignoring.')
			return

		logging.info('Async GET response received.')

		jsonData = response.payload.decode("utf-8")

		if hasattr(response, "requested_path") and len(response.requested_path) >= 3:
			dataType = response.requested_path[2]

			if dataType == ConfigConst.ACTUATOR_CMD:
				logging.info("ActuatorData received: %s", jsonData)

				try:
					if jsonData.strip().startswith("{"):
						try:
							ad = DataUtil().jsonToActuatorData(jsonData)
							if self.dataMsgListener:
								self.dataMsgListener.handleActuatorCommandMessage(ad)
						except Exception as e:
							logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
							traceback.print_exception(type(e), e, e.__traceback__)
					else:
						logging.info("GET response is not JSON. Message: %s", jsonData)

					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except Exception as e:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					traceback.print_exception(type(e), e, e.__traceback__)
			else:
				logging.info("Response data received. Payload: %s", jsonData)
		else:
			logging.info("Response data received. Payload: %s", jsonData)

	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		logging.info("Discovering remote resources...")

		return self.sendGetRequest(
			resource=None,
			name='.well-known/core',
			enableCON=False,
			timeout=timeout
		)

	def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			# Construir la URI completa correctamente
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath
			else:
				resourcePath = name  # ya es una URI completa

			#logging.info("Issuing Async POST to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handlePostRequest(
					resourcePath=resourcePath,
					payload=payload,
					enableCON=enableCON
				)
			)
		else:
			logging.warning("Can't issue Async POST - no path or path list provided.")

	async def _handlePostRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			payloadBytes = b''

			# Decide which encoding to use - can also load from config
			if payload:
				payloadBytes = payload.encode('utf-8')

			msg = Message(mtype=msgType, payload=payloadBytes, code=Code.POST, uri=resourcePath)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onPostResponse(responseData)

		except Exception as e:
			logging.warning("Failed to process POST request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)

	def _onPostResponse(self, response):
		if not response:
			logging.warning('POST response invalid. Ignoring.')
			return

		#logging.info('POST response received: %s', response.payload)

	def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False,
					   payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			# Construir la URI completa correctamente
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath  # self.uriPath ya incluye el host y puerto
			else:
				resourcePath = name  # ya es una URI completa, como 'coap://localhost:5683/...'

			#logging.info("Issuing Async PUT to path: " + resourcePath)

			try:
				asyncio.get_event_loop().run_until_complete(
					self._handlePutRequest(
						resourcePath=resourcePath,
						payload=payload,
						enableCON=enableCON
					)
				)
			except Exception as e:
				logging.warning("Error during Async PUT execution.")
				traceback.print_exception(type(e), e, e.__traceback__)
		else:
			logging.warning("Can't issue Async PUT - no path or path list provided.")

	async def _handlePutRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
		try:
			msgType = NON
			if enableCON:
				msgType = CON

			# Validar y codificar payload
			payloadBytes = b''
			if payload:
				if isinstance(payload, str):
					payloadBytes = payload.encode('utf-8')
				else:
					# Por si recibe un dict u otro objeto JSON
					import json
					payloadBytes = json.dumps(payload).encode('utf-8')

			msg = Message(mtype=msgType, code=Code.PUT, uri=resourcePath, payload=payloadBytes)
			req = self.coapClient.request(msg)

			responseData = await req.response
			self._onPutResponse(responseData)

		except Exception as e:
			logging.warning("Failed to process PUT request for path: " + str(resourcePath))
			traceback.print_exception(type(e), e, e.__traceback__)

	def _onPutResponse(self, response):
		if not response:
			logging.warning('PUT response invalid. Ignoring.')
			return

		try:
			responseText = response.payload.decode('utf-8')
			#logging.info('PUT response received: %s', responseText)
		except Exception as e:
			logging.warning('Failed to decode PUT response.')
			traceback.print_exception(type(e), e, e.__traceback__)

	def setDataMessageListener(self, listener: IDataMessageListener = None):
		self.dataMsgListener = listener

	def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None) -> str:
		resourcePath = ""
		hasResource = False

		if resource:
			resourcePath = resourcePath + resource.value
			hasResource = True

		if name:
			if hasResource:
				resourcePath = resourcePath + '/'
			resourcePath = resourcePath + name

		return resourcePath

	def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
		if resource or name:
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath
			else:
				resourcePath = name

			if resourcePath in self.observeRequests:
				logging.warning("Already observing resource %s. Ignoring start observe request.", resourcePath)
				return False

			try:
				asyncio.get_event_loop().run_until_complete(
					asyncio.ensure_future(self._handleStartObserveRequest(resourcePath))
				)
				return True
			except Exception as e:
				logging.warning("Failed to start observer.")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't issue Async OBSERVE - GET - no path or path list provided.")
			return False

	def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			if resource or (name and not name.startswith("coap://")):
				resourcePath = self._createResourcePath(resource, name)
				resourcePath = self.uriPath + resourcePath
			else:
				resourcePath = name

			if resourcePath not in self.observeRequests:
				logging.warning("Resource %s not being observed. Ignoring stop observe request.", resourcePath)
				return False

			try:
				asyncio.get_event_loop().run_until_complete(
					self._handleStopObserveRequest(resourcePath)
				)
				return True
			except Exception as e:
				logging.warning("Failed to stop observer.")
				traceback.print_exception(type(e), e, e.__traceback__)
				return False
		else:
			logging.warning("Can't cancel OBSERVE - GET - no path provided.")
			return False

	async def _handleStartObserveRequest(self, resourcePath: str = None):
		logging.info('Handle start observe invoked. Waiting for each input: ' + resourcePath)

		try:
			msg = Message(code=Code.GET, uri=resourcePath, observe=0)
			req = self.coapClient.request(msg)
			self.observeRequests[resourcePath] = req

			responseData = await req.response
			self._onGetResponse(responseData)

			async for responseData in req.observation:
				self._onGetResponse(responseData)
				break  # Solo procesamos la primera respuesta
		except Exception as e:
			logging.warning("Failed to execute OBSERVE - GET. Recovering...")
			traceback.print_exception(type(e), e, e.__traceback__)

	async def _handleStopObserveRequest(self, resourcePath: str = None, ignoreErr: bool = False):
		if resourcePath in self.observeRequests:
			logging.info('Handle stop observe invoked: ' + resourcePath)
			try:
				observeRequest = self.observeRequests[resourcePath]
				observeRequest.observation.cancel()
			except Exception as e:
				if not ignoreErr:
					logging.warning("Failed to cancel OBSERVE - GET: " + resourcePath)
					traceback.print_exception(type(e), e, e.__traceback__)

			try:
				del self.observeRequests[resourcePath]
			except Exception as e:
				if not ignoreErr:
					logging.warning("Failed to remove observable from list: " + resourcePath)
					traceback.print_exception(type(e), e, e.__traceback__)
		else:
			logging.warning('Resource not currently under observation. Ignoring: ' + resourcePath)

	def _initClient(self):
		asyncio.get_event_loop().run_until_complete(self._initClientContext())

	async def _initClientContext(self):
		try:
			logging.info("Creating CoAP client for URI path: " + self.uriPath)

			self.coapClient = await Context.create_client_context()

			logging.info('Client context created. Will invoke resources at: ' + self.uriPath)

		except Exception as e:
			# obviously, this is a critical failure - you may want to handle this differently
			logging.error("Failed to create CoAP client to URI path: " + self.uriPath)
			traceback.print_exception(type(e), e, e.__traceback__)
