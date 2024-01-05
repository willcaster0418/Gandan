import struct, sys, time, logging, traceback
import socket
import re

try:
	from .GandanMsg import *
	from .MMAP  import *
except Exception as e:
	from GandanMsg import *
	from MMAP  import *

class GandanSub:
	def __init__(self, ip, port, _cmd, _io, path=None): # _io is wating time 
		if path == None:
			self.type_    = 0
			self.ip_port_ = (ip, port)
			self.io_	  = _io
			self.cmd_	 = _cmd
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)
		else:
			size = 5000*20000
			item_size = 20000
			self.type_    = 1
			self.path_    = path
			self.cmd_     = _cmd
			self.topic    = _cmd.split('_')[1]
			#open shm
			self.mmap     = MMAP(path+"/"+self.topic, size, item_size)

	def sub_shm(self, cb, obj=None, hb_cb=None):
		msg_list = self.mmap.readp()
		#print(len(msg_list))
		ret = ""
		for msg in msg_list:
			if obj == None:
				ret = cb(str(msg, 'utf-8'))
			else:
				ret = cb(str(msg,'utf-8'), obj)
		return ret

	def sub(self, cb, obj=None, hb_cb=None):
		_h = None
		if self.type_ == 0:
			try:
				_h = GandanMsg.recv(None, self.s)
				if obj == None:
					return cb(_h)
				return cb(_h, obj)
			except Exception as e:
				pass
		elif self.type_ == 1:
			return self.sub_shm(cb, obj, hb_cb)

	def close(self):
		if self.type_ == 0:
			self.s.close()
		elif self.type_ == 1:
			self.mmap.f.close()

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
