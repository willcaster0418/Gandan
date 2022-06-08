#--*--coding:utf-8--*--
import struct, sys, time, re
from ast import literal_eval
import threading, logging, socket

class GandanMsg:
	def __init__(self, _cmd, _dat): 
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
	def send_websocket(self, _sock, _cmd, _msg):
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
