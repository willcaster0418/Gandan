#--*--coding=utf-8--*--
import struct, sys, time, re
from ast import literal_eval
from datetime import datetime
import socket
import threading, logging
import traceback

from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

class Gandan:
	def __init__(self, ip_port, path, size, item_size):
		self.ip_port = ip_port
		self.path_ = path
		self.sz_   = size
		self.isz_  = item_size
		self.pub_topic_ = {}
		self.sub_topic_ = {}
		self.rlist_ = []
		self.p_reg_lock = threading.Lock()
		self.s_reg_lock = threading.Lock()

	def setup_log(self, path):
		l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(funcName)s^%(lineno)d^%(message)s'
		d_format = '%Y-%m-%d^%H:%M:%S'
		logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=logging.DEBUG)

	def log(self, _d):
		logging.info(_d)

	def handler(self, _req):
		_p = True
		_h = None
		_cnt_none = 0
		_pubsub = ""
		while(_p):
			try:
				_h = GandanMsg.recv(None, _req)
				(_cmd, _msg)	  = (_h.cmd_, _h.dat_)
				[_pubsub, _topic] = _cmd.split("_")
			except Exception as e:
				_type, _value, _traceback = sys.exc_info()
				self.log("#Error" + str(_type) + str(_value))
				for _err_str in traceback.format_tb(_traceback):
					self.log(_err_str)
				if str(e) in ['convert']:
					continue
				else:
					_p = False
					continue

			#Note : PUB/SUB가 등록 시 경쟁하는 상황이 발생가능
			if _pubsub == "PUB": 
				if not _topic in self.pub_topic_.keys():
					self.p_reg_lock.acquire()
					_p = self.pub(_req, _topic, _msg)
					self.p_reg_lock.release()
				else:
					_p = self.pub(_req, _topic, _msg)
				continue

			if _pubsub == "SUB":
				if not _topic in self.sub_topic_.keys():
					self.s_reg_lock.acquire()
					_p = self.sub(_req, _topic, _msg)
					self.s_reg_lock.release()
				else: 
					_p = self.sub(_req, _topic, _msg)
				break
		try:
			if _pubsub == "PUB":
				_req.close()
		except Exception as e:
			self.log("#Error socket close for %s" % str(_req))

	def pub(self, _req, _topic, _msg):
		try:
			_path = self.path_+_topic
			_pub = None

			if (_topic == "ORDER" or _topic == "OM") and _req.getsockname()[0] != '127.0.0.1':
				_req.close()
				return False

			if not _topic in self.pub_topic_.keys(): 
				self.pub_topic_[_topic] = []
				self.pub_topic_[_topic].append(RoboMMAP(_path, _topic, self.mon, self.sz_, self.isz_))
				_pub = self.pub_topic_[_topic][-1]
				_pub.start()
				self.log("PUB que path : %s monitor start,r[%d]w[%d]" % (_path, _pub.r(), _pub.w()) + ", TOPIC : %s" % _topic)
			else:
				_pub = self.pub_topic_[_topic][-1]

			if Gandan.version(None) < 3:
				_pub.writep(bytes(_msg))
			else:
				_pub.writep(bytes(_msg,'utf-8'))
		except Exception as e:
			#self.log("#Error During PUB[%s], " % _topic + "[%s..]" % _msg.strip()[0:50] + " r[%d]w[%d]" % (_pub.r(), _pub.w()))
			self.log(str(e))
			return False

		self.log("PUB[%s], " % _topic + "^%s^%d" % (_msg.strip(), len(_msg.strip())) + " r[%d]w[%d]" % (_pub.r(), _pub.w()))
		return True

	def sub(self, _req, _topic, _msg):
		try:
			if not _topic in self.sub_topic_.keys():
				self.sub_topic_[_topic] = []
				self.sub_topic_[_topic].append(_req)
				self.log("_topic : %s is created for SUB" % _topic)
			else:
				self.sub_topic_[_topic].append(_req)
				self.log("_topic : %s is appended for SUB" % _topic)
		except Exception as e:
			return False
		return True

	def start(self):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.log("------------ MW Gandan Start --------------")
			s.bind(self.ip_port)
			s.listen(10)
			#Todo : 소켓 당 쓰레드를 띄우는 대신 다중 IO로 변경
			while True:
				try:
					_r, _a = s.accept()
					self.rlist_.append(_r)
					t = threading.Thread(target = self.handler, args = (_r, ))
					t.start()
				except Exception as e:
					self.log("%s"%str(e)+":%s"%str(e))
					break

	def mon(self, _topic, _data):
		if not _topic in self.sub_topic_.keys():
			return

		error_req_list = []

		#http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm
		for i, _req in enumerate(self.sub_topic_[_topic]):
			try:
				for d in _data:
					if Gandan.version(None) < 3:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d))
					else:
						GandanMsg.send(None, _req, "DATA_"+_topic, str(d,'utf-8'))
			except Exception as e:
				error_req_list.append(_req)
				continue

		for _req in error_req_list:
			self.sub_topic_[_topic].remove(_req)

		if len(error_req_list) > 0:
			self.log("#Error in SUB [%s] : %d request is removed" % (_topic, len(error_req_list)))

	@staticmethod
	def version(self):
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))

if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8888)
		h = Gandan(l_ip_port, "/home/robosys/Gandan/MW/que/", 10000, 1000)
		h.setup_log(datetime.now().strftime("/home/robosys/Gandan/MW/log/%Y%m%d")+".Gandan.log")
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

