
from nintendo.nex import service, common, streams, kerberos, errors
import hashlib
import struct

import logging
logger = logging.getLogger(__name__)


class AuthenticationError(Exception): pass


class AuthenticationInfo(common.Data):
	def __init__(self, token, server_version):
		self.token = token
		self.server_version = server_version
		
	def get_name(self):
		return "AuthenticationInfo"

	def save(self, stream):
		stream.string(self.token)
		stream.u32(3)
		stream.u8(1)
		stream.u32(self.server_version)
common.DataHolder.register(AuthenticationInfo, "AuthenticationInfo")


class NintendoLoginData(common.Data):
	def __init__(self, token):
		self.token = token
		
	def get_name(self):
		return "NintendoLoginData"
		
	def save(self, stream):
		stream.string(self.token)
common.DataHolder.register(NintendoLoginData, "NintendoLoginData")


class AccountExtraInfo(common.Data):
	def __init__(self, unk_u32_1, unk_u32_2, unk_u32_3, token):
		self.unk_u32_1 = unk_u32_1
		self.unk_u32_2 = unk_u32_2
		self.unk_u32_3 = unk_u32_3
		self.token = token

	def get_name(self):
		return "AccountExtraInfo"

	def save(self, stream):
		stream.u32(self.unk_u32_1)
		stream.u32(self.unk_u32_2)
		stream.u32(self.unk_u32_3)
		stream.string(self.token)

	def load(self, stream):
		self.unk_u32_1 = stream.u32()
		self.unk_u32_2 = stream.u32()
		self.unk_u32_3 = stream.u32()
		self.token = stream.string()
common.DataHolder.register(AccountExtraInfo, "AccountExtraInfo")


class RVConnectionData(common.Structure):
	def get_version(self):
		return 1
	
	def load(self, stream):
		self.main_station = stream.stationurl()
		self.special_protocols = stream.list(stream.u8)
		self.special_station = stream.stationurl()
		
		self.server_time = None
		if self.version >= 1:
			self.server_time = stream.datetime()

			
class KeyDerivationOld:
	def __init__(self, base_count, pid_count):
		self.base_count = base_count
		self.pid_count = pid_count
		
	def derive_key(self, password, pid):
		key = password
		for i in range(self.base_count + pid % self.pid_count):
			key = hashlib.md5(key).digest()
		return key
		
		
class KeyDerivationNew:
	def __init__(self, base_count, pid_count):
		self.base_count = base_count
		self.pid_count = pid_count
		
	def derive_key(self, password, pid):
		key = password
		for i in range(self.base_count):
			key = hashlib.md5(key).digest()
			
		key += struct.pack("<Q", pid)
		for i in range(self.pid_count):
			key = hashlib.md5(key).digest()
			
		return key


class AuthenticationClient(service.ServiceClient):
	
	METHOD_LOGIN = 1
	METHOD_LOGIN_EX = 2
	METHOD_REQUEST_TICKET = 3
	METHOD_GET_PID = 4
	METHOD_GET_NAME = 5
	METHOD_LOGIN_WITH_CONTEXT = 6
	
	PROTOCOL_ID = 0xA
	
	def __init__(self, backend):
		super().__init__(backend, service.ServiceClient.AUTHENTICATION)
		self.settings = backend.settings
		if self.settings.get("kerberos.key_derivation") == 0:
			self.key_derivation = KeyDerivationOld(65000, 1024)
		else:
			self.key_derivation = KeyDerivationNew(1, 1)
		
	def login(self, username, password):
		logger.info("Authentication.login(%s, %s)", username, password)
		#--- request ---
		stream, call_id = self.init_request(self.PROTOCOL_ID, self.METHOD_LOGIN)
		stream.string(username)
		self.send_message(stream)
		
		#--- response ---
		self.handle_login_result(call_id, password)
		
	def login_ex(self, username, password, auth_info):
		logger.info("Authentication.login_ex(%s, %s, %s)", username, password, auth_info.__class__.__name__)
		#--- request ---
		stream, call_id = self.init_request(self.PROTOCOL_ID, self.METHOD_LOGIN_EX)
		stream.string(username)
		stream.anydata(auth_info)
		self.send_message(stream)
		
		#--- response ---
		self.handle_login_result(call_id, password)
		
	def handle_login_result(self, call_id, password):
		stream = self.get_response(call_id)
		result = stream.u32()
		if result & 0x80000000:
			raise AuthenticationError("Login failed (%s)" %errors.error_names.get(result, "unknown error"))
			
		self.pid = stream.uint()
		kerberos_data = stream.buffer()
		self.secure_station = stream.extract(RVConnectionData).main_station
		server_name = stream.string()
		
		kerberos_key = self.key_derivation.derive_key(password.encode("ascii"), self.pid)
		self.kerberos_encryption = kerberos.KerberosEncryption(kerberos_key)
		if not self.kerberos_encryption.check_hmac(kerberos_data):
			raise AuthenticationError("Kerberos key validation failed (incorrect password)")

		logger.info("Authentication.login(_ex) -> (%08X, %s, %s)", self.pid, self.secure_station, server_name)
		
	def request_ticket(self):
		logger.info("Authentication.request_ticket()")
		#--- request ---
		stream, call_id = self.init_request(self.PROTOCOL_ID, self.METHOD_REQUEST_TICKET)
		stream.uint(self.pid)
		stream.uint(self.secure_station["PID"])
		self.send_message(stream)

		#--- response ---
		stream = self.get_response(call_id)
		result = stream.u32()
		if result & 0x80000000:
			raise AuthenticationError("Ticket request failed (%s)" %errors.error_names.get(result, "unknown error"))

		encrypted_ticket = stream.buffer()
		ticket_stream = streams.StreamIn(self.kerberos_encryption.decrypt(encrypted_ticket), self.backend.settings)
		ticket_key = ticket_stream.read(self.settings.get("kerberos.key_size"))
		ticket_stream.uint() #Unknown
		ticket_buffer = ticket_stream.buffer()

		logger.info("Authentication.request_ticket -> %s", ticket_key.hex())
		return kerberos.Ticket(ticket_key, ticket_buffer)
		
	def get_pid(self, name):
		logger.info("Authentication.get_pid(%s)", name)
		#--- request ---
		stream, call_id = self.init_request(self.PROTOCOL_ID, self.METHOD_GET_PID)
		stream.string(name)
		self.send_message(stream)
		
		#--- response ---
		stream = self.get_response(call_id)
		pid = stream.uint()
		logger.info("Authentication.get_pid -> %i", pid)
		return pid
		
	def get_name(self, id):
		logger.info("Authentication.get_name(%i)", id)
		#--- request ---
		stream, call_id = self.init_request(self.PROTOCOL_ID, self.METHOD_GET_NAME)
		stream.uint(id)
		self.send_message(stream)
		
		#--- response ---
		stream = self.get_response(call_id)
		name = stream.string()
		logger.info("Authentication.get_name -> %s", name)
		return name
