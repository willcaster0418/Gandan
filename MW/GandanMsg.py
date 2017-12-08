import struct, sys, time, re
from ast import literal_eval
from datetime import datetime
import threading, logging, socket

class GandanMsg:
	def __init__(self, _cmd, _dat): 
		self.total_size = 12 + len(_cmd) + len(_dat)
		(self.sep_, self.cmd_, self.dat_) = (b'#', _cmd, _dat)

	def __bytes__(self):
		_b =  self.sep_
		_b += struct.pack("!i", len(self.cmd_) + len(self.dat_)+8)
		if GandanMsg.version(None) < 300:
			_b += struct.pack("!i", len(self.cmd_)) + bytes(self.cmd_)
			_b += struct.pack("!i", len(self.dat_)) + bytes(self.dat_)
		else:
			_b += struct.pack("!i", len(self.cmd_)) + bytes(self.cmd_, "utf-8")
			_b += struct.pack("!i", len(self.dat_)) + bytes(self.dat_, "utf-8")
		return _b
	
	def __str__(self):
		return self.cmd_+":"+self.dat_

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

	@staticmethod
	def conv2(self, _b):
		_c_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_c    = str(_b[:_c_sz]); _b = _b[_c_sz:]
		_d_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_d	  = str(_b[:_d_sz])     
		return GandanMsg(_c, _d)

	@staticmethod
	def conv3(self, _b):
		_c_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_c    = str(_b[:_c_sz], 'utf-8'); _b = _b[_c_sz:]
		_d_sz = struct.unpack("!i", _b[:4])[0]; _b = _b[4:]
		_d	  = str(_b[:_d_sz], 'utf-8')     
		return GandanMsg(_c, _d)

	@staticmethod
	def send(self, _sock, _cmd, _msg):
		_h = GandanMsg(_cmd, _msg)
		if GandanMsg.version(None) < 300:
			_sock.send(_h.__bytes__())
		else:
			_sock.send(bytes(_h))

	@staticmethod
	def recv(self, _sock):
		_b = ''; _sz = 0;
		while True:
			try:
				_b = _sock.recv(1)
			except socket.timeout as e:
				raise Exception('timeout')

			if len(_b) == 0:
				raise Exception('conn')
			
			if _b == b'#': 
				break
		try:
			_b   = _sock.recv(4)  
		except socket.timeout as e:
			raise Exception('timeout')

		try:
			_sz  = struct.unpack("!i", _b)[0]
		except socket.timeout as e:
			raise Exception('convert')

		try:
			_b   = _sock.recv(_sz)
		except socket.timeout as e:
			raise Exception('timeout')

		if len(_b) == 0:
			raise Exception('conn')
		try:
			if GandanMsg.version(None) < 300:
				return GandanMsg.conv2(None, _b)
			else:
				return GandanMsg.conv3(None, _b)
		except Exception as e:
			return None
