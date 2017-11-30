import struct, sys, time, logging
import socket
import re
from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class GandanSub:
	def __init__(self, ip, port, _cmd, _io): # _io is wating time 
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_port_ = (ip, port)
		self.io_	  = _io
		self.cmd_	 = _cmd
		self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)

	def sub(self, cb):
		try:
			_h = GandanMsg.recv(None, self.s)

			if _h.dat_.strip() == "HB":
				return

			cb(_h)

		except Exception as e:
			if str(e) in ["timeout", "convert"]:
				return
			elif str(e) == "conn":
				try:
					print(str(e))
					self.s.close()
					self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)

				except Exception as e:
					return
			else:
				return

	def close(self):
		self.s.close()

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

	@staticmethod
	def connect(self, _sock, _ip_port, _cmd, _io):
		_sock.connect(_ip_port)
		_sock.settimeout(_io)
		_h = GandanMsg(_cmd, "INIT")
		_sock.send(bytes(_h))
		return _sock

def callback(_h):
	print(_h)

if __name__ == "__main__":
	_h = GandanSub("127.0.0.1", 8888, sys.argv[1])
	_h.sub(callback)
