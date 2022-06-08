import struct, sys, time, logging, traceback
import socket
import re

from .GandanMsg import *
from .MMAP  import *

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

				if _h.dat_.strip() == "HB":
					#logging.info("------------------HB----------------[%s]" % self.cmd_)
					if hb_cb == None:
						return 1
					if hb_cb(obj, _h) == -1:
						raise Exception("conn")
				else:
					if obj == None:
						return cb(_h)
					return cb(_h, obj)

				return 1

			except Exception as e:
				if not str(e) in ["timeout"]:
					_type, _value, _traceback = sys.exc_info()
					logging.info("#Error" + str(_type) + str(_value))
					for _err_str in traceback.format_tb(_traceback):
						logging.info(_err_str)
					try:
						logging.info(str(_h).strip())
					except Exception as er:
						logging.info(str(er))

				if str(e) in ["timeout"]:
					if hb_cb != None and hb_cb(obj, None) == -1:
						e = Exception("conn")
					return None
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
