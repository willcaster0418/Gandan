import struct, sys, time, logging, traceback
import socket
import re
from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class GandanSub:
	def __init__(self, ip, port, _cmd, _io): # _io is wating time 
		self.ip_port_ = (ip, port)
		self.io_	  = _io
		self.cmd_	 = _cmd
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)

	def sub(self, cb, obj=None):
		try:
			_h = GandanMsg.recv(None, self.s)

			if _h.dat_.strip() == "HB":
				logging.info("Heart Beat...[%s]" % self.cmd_)
				return 1
			else:
				try:
					if obj == None:
						cb(_h)
						return 1
					cb(_h, obj)
					return 1
				except Exception as e:
					_type, _value, _traceback = sys.exc_info()
					logging.info("#Error" + str(_type) + str(_value))
					for _err_str in traceback.format_tb(_traceback):
						logging.info(_err_str)
		except Exception as e:
			if str(e) in ["timeout"]:
				return 1
			elif str(e) in ["convert"]:
				return -2
			elif str(e) in ["conn"]:
				logging.info(str(e)+": #Error Try to reconnect")
				while True:
					try:
						_tmp_socket = self.s
						self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)
						logging.info("reconnect SUCC")
						return 1
					except Exception as e:
						logging.info(str(e)+" : reconnect FAIL")
					finally:
						try:
							_tmp_socket.close()
							logging.info("socket close succ")
						except Exception as e:
							logging.info("socket close fail")
						finally:
							time.sleep(60)
			else:
				logging.info(str(e)+":unknown error")

	def close(self):
		self.s.close()

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))

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
