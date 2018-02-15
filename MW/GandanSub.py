import struct, sys, time, logging, traceback, datetime
import socket
import re

from .GandanMsg import *

class GandanSub:
	def __init__(self, ip, port, _cmd, _io): # _io is wating time 
		self.ip_port_ = (ip, port)
		self.io_	  = _io
		self.cmd_	 = _cmd
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)

	def sub(self, cb, obj=None, hb_cb=None):
		try:
			_h = GandanMsg.recv(None, self.s)

			if _h.dat_.strip() == "HB":
				#logging.info("------------------HB----------------[%s]" % self.cmd_)
				if hb_cb == None:
					return 1
				if hb_cb(obj, _h) == -1:
					raise Exception("conn")
			else:
				if obj == None:
					cb(_h)
					return 1
				cb(_h, obj)

			return 1

		except Exception as e:
			if not str(e) in ["timeout"]:
				_type, _value, _traceback = sys.exc_info()
				logging.info("#Error" + str(_type) + str(_value))
				for _err_str in traceback.format_tb(_traceback):
					logging.info(_err_str)

			if str(e) in ["timeout"]:
				if hb_cb != None and hb_cb(obj, None) == -1:
					e = Exception("conn")
			elif str(e) in ["convert"]:
				return -2

			if str(e) in ["conn"]:
				logging.info(str(e)+": #Error Try to reconnect")
				display_cnt = 0
				while True:
					try:
						self.s.close()
						logging.info("#SUCC : previous socket close")
					except Exception as e:
						logging.info("#FAIL : previous socket close")
					finally:
						try:
							self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							self.s = GandanSub.connect(None, self.s, self.ip_port_, self.cmd_, self.io_)
							logging.info("#SUCC : new socket connect")
							break
						except Exception as e:
							if display_cnt % 100 == 0:
								logging.info("#FAIL : new socket connect")
						finally:
							display_cnt = display_cnt + 1
							time.sleep(0.1)

	def close(self):
		self.s.close()

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
