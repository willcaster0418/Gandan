#--*--coding:utf-8--*--
import struct, sys, time, re
from ast import literal_eval
import threading, logging, socket
import socket, re, threading, logging
import hashlib, base64, json

class GandanMsg:
	def __init__(self, _cmd, _dat):
		# 왜 12를 더해주는가? 숫자 3개??
		if GandanMsg.version() < 3:
			self.total_size = 12 + len(bytes(_cmd)) + len(bytes(_dat))
		else:
			self.total_size = 12 + len(bytes(_cmd, "utf-8")) + len(bytes(_dat,"utf-8"))
		(self.sep_, self.cmd_, self.dat_) = (b'#', _cmd, _dat)

	def __bytes__(self):
		_b =  self.sep_
		_b += struct.pack("!i", self.total_size-4)
		if GandanMsg.version() < 3:
			_b += struct.pack("!i", len(bytes(self.cmd_))) + bytes(self.cmd_)
			_b += struct.pack("!i", len(bytes(self.dat_))) + bytes(self.dat_)
		else:
			_b += struct.pack("!i", len(bytes(self.cmd_, "utf-8"))) + bytes(self.cmd_, "utf-8")
			_b += struct.pack("!i", len(bytes(self.dat_, "utf-8"))) + bytes(self.dat_, "utf-8")
		return _b
	
	def __str__(self):
		return str(self.total_size)+":"+self.cmd_+":"+self.dat_

	@staticmethod
	def version():
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))

	@staticmethod
	def conv2(self, _b):
		_c_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_c	= str(_b[:_c_sz]); _b = _b[_c_sz:]
		_d_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_d	  = str(_b[:_d_sz])	 
		return GandanMsg(_c, _d)

	@staticmethod
	def conv3(self, _b):
		_c_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_c	= str(_b[:_c_sz], 'utf-8'); _b = _b[_c_sz:]
		_d_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_d	  = str(_b[:_d_sz], 'utf-8')	 
		return GandanMsg(_c, _d)

	@staticmethod
	def send(self, _sock, _cmd, _msg):
		_h = GandanMsg(_cmd, _msg)
		if GandanMsg.version() < 3:
			_sock.send(_h.__bytes__())
		else:
			_sock.send(bytes(_h))

	@staticmethod
	def handshake(self, _sock):
		request = _sock.recv(2048)
		m = re.match('[\\w\\W]+Sec-WebSocket-Key: (.+)\r\n[\\w\\W]+\r\n\r\n', str(request, 'utf-8'))

		key = m.group(1)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11' #웹소켓 고유 GUID
		 
		response  = "HTTP/1.1 101 Switching Protocols\r\n"
		response += "Upgrade: websocket\r\n"
		response += "Connection: Upgrade\r\n"
		response += "Sec-WebSocket-Accept: %s\r\n\r\n"
		r = response % str(base64.b64encode(hashlib.sha1(bytes(key,'utf-8')).digest()),'utf-8')
		_sock.send(bytes(r, 'utf-8'))

		cmd = (str(request, 'ascii').split("\r\n")[0].split(" ")[0])
		topic = (str(request, 'ascii').split("\r\n")[0].split(" ")[1])

		return (cmd, topic, "websocket")

	@staticmethod
	def send_websocket(self, _sock, _msg):
		#안그래도 느린넘한테 보낼 때는 strip을 해서보냄
		#data = bytearray(_msg.strip().encode('utf-8'))
		data = bytearray(_msg.encode('utf-8'))
		if len(data) > 126:
			data = bytearray([ord(b'\x81'), 126]) + bytearray(struct.pack('>H', len(data))) + data
			#logging.info("> %s" % data)
		else:
			data = bytearray([ord(b'\x81'), len(data)]) + data
			#logging.info("%s" % data)
		_sock.send(data)

	@staticmethod
	def recv(self, _sock):
		_b = ''; _sz = 0;
		while True:
			try:
				_b = _sock.recv(1)
			except socket.timeout as e:
				raise Exception('timeout')

			if len(_b) == 0:
				_sock.close()
				raise Exception('conn')
			
			if _b == b'#': 
				break
		try:
			_b   = _sock.recv(4)  
		except socket.timeout as e:
			raise Exception('timeout')

		try:
			_sz  = struct.unpack("!i", _b)[0]
			#logging.info("size of recv packet from socket => [%d]" % _sz)
		except Exception as e:
			raise Exception('convert')

		try:
			_b   = _sock.recv(_sz)
		except Exception as e:
			raise Exception('timeout')

		if len(_b) == 0:
			raise Exception('conn')
		try:
			if GandanMsg.version() < 3:
				return GandanMsg.conv2(None, _b)
			else:
				return GandanMsg.conv3(None, _b)
		except Exception as e:
			logging.info(str(e))
			raise Exception('convert')

	@staticmethod
	def recvwebsocket(self, _sock):
		data= bytearray(_sock.recv(1))
		if len(data) == 0:
			return None, None
		first_byte = data[0]
		FIN = (0xFF & first_byte) >> 7
		opcode = (0x0F & first_byte)
		second_byte = bytearray(_sock.recv(1))[0]
		mask = (0xFF & second_byte) >> 7
		payload_len = (0x7F & second_byte)
		if opcode < 3:
			if (payload_len == 126):
				payload_len = struct.unpack_from('>H', bytearray(_sock.recv(2)))[0]
			elif (payload_len == 127):
				payload_len = struct.unpack_from('>Q', bytearray(_sock.recv(8)))[0]
			if mask == 1:
				masking_key = bytearray(_sock.recv(4))
			masked_data = bytearray(_sock.recv(payload_len))
			if mask == 1:
				data = [masked_data[i] ^ masking_key[i%4] for i in range(len(masked_data))]
			else:
				data = masked_data
		else:
			return opcode, bytearray(b'\x00')
		return opcode, bytearray(data)
	

	@staticmethod
	def recvall(self, _sock, status = 0, protocol = "raw", msg = None):
		acc_b = b''; _b = b''; _sz = 0; p = 0; m = b'';
		if status == 0 or (status !=0 and protocol == "raw"):
			while True:
				try:
					_b = _sock.recv(1)
				except socket.timeout as e:
					raise Exception('timeout')
			
				if len(_b) == 0:
					_sock.close()
					raise Exception('conn')
				
				
				if _b == b'#':
					p = 0
					break
			
				acc_b += _b
				m = re.match('[\\w\\W]+Sec-WebSocket-Key: (.+)\r\n[\\w\\W]+\r\n\r\n', str(acc_b, 'utf-8'))
				
				if m != None:
					p = 1
					break
		else:
			opcode, data = GandanMsg.recvwebsocket(None, _sock)
			if msg != None:
				msg.dat_ = data.decode("utf-8")
			return msg, "websocket"


		if p == 0:
			try:
				_b   = _sock.recv(4)  
			except socket.timeout as e:
				raise Exception('timeout')
			
			try:
				_sz  = struct.unpack("!i", _b)[0]
				#logging.info("size of recv packet from socket => [%d]" % _sz)
			except Exception as e:
				raise Exception('convert')
			
			try:
				_b   = _sock.recv(_sz)
			except Exception as e:
				raise Exception('timeout')
			
			if len(_b) == 0:
				raise Exception('conn')
			try:
				if GandanMsg.version() < 3:
					return GandanMsg.conv2(None, _b), "raw"
				else:
					return GandanMsg.conv3(None, _b), "raw"
			except Exception as e:
				logging.info(str(e))
				raise Exception('convert')
		else:
			request = acc_b
			key = m.group(1)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11' #웹소켓 고유 GUID
			response  = "HTTP/1.1 101 Switching Protocols\r\n"
			response += "Upgrade: websocket\r\n"
			response += "Connection: Upgrade\r\n"
			response += "Sec-WebSocket-Accept: %s\r\n\r\n"
			r = response % str(base64.b64encode(hashlib.sha1(bytes(key,'utf-8')).digest()),'utf-8')
			_sock.send(bytes(r, 'utf-8'))
			url = (str(request, 'ascii').split("\r\n")[0].split(" ")[1])
			_, cmd, topic = url.split("/")
			# todo GandanMsg with cmd, topic
			return GandanMsg(cmd+"_"+topic, ''), "websocket"

		return None

	@staticmethod
	def recv_websocket(self, _sock):
		data= bytearray(_sock.recv(1))
		if len(data) == 0:
			return None, None
		first_byte = data[0]
		FIN = (0xFF & first_byte) >> 7
		opcode = (0x0F & first_byte)
		second_byte = bytearray(_sock.recv(1))[0]
		mask = (0xFF & second_byte) >> 7
		payload_len = (0x7F & second_byte)
		if opcode < 3:
			if (payload_len == 126):
				payload_len = struct.unpack_from('>H', bytearray(_sock.recv(2)))[0]
			elif (payload_len == 127):
				payload_len = struct.unpack_from('>Q', bytearray(_sock.recv(8)))[0]
			if mask == 1:
				masking_key = bytearray(_sock.recv(4))
			masked_data = bytearray(_sock.recv(payload_len))
			if mask == 1:
				data = [masked_data[i] ^ masking_key[i%4] for i in range(len(masked_data))]
			else:
				data = masked_data
		else:
			raise Exception("disconnect")

		if GandanMsg.version() < 3:
			return GandanMsg.conv2(None, data)
		else:
			return GandanMsg.conv3(None, data)
	
