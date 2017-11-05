import struct, sys
import socket
import re
from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class GandanSub:
	def __init__(self, ip, port, _cmd, _io): # 0 : block 1 : non-block
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip, port))
		if _io == 1:
			self.s.settimeout(0.001)
		_h = GandanMsg(_cmd, "INIT")
		self.s.send(bytes(_h))

	def sub(self, cb):
		try:
			_h = GandanMsg.recv(None, self.s)
			cb(_h)
		except socket.timeout as e:
			return

	def close(self):
		self.s.close()

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0]).zfill(3))

def callback(_h):
	print(_h)

if __name__ == "__main__":
	_h = GandanSub("127.0.0.1", 8888, sys.argv[1])
	_h.sub(callback)
