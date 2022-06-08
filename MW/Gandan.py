#--*--coding=utf-8--*--
import struct, sys, time, re
from ast import literal_eval
from datetime import datetime
import socket
import threading, logging
import traceback

from .GandanMsg import *
from .MMAP  import *

class Gandan:
	def __init__(self, ip_port, path, size, item_size, debug=False):
		self.ip_port = ip_port
		self.path    = path
		self.sz      = size
		self.isz     = item_size

		self.pub_topic = {}
		self.sub_topic = {}
		self.sub_topic_websocket = {}
		self.rlist     = []

		self.debug = debug

		self.pub_lock_dict = {}

	@staticmethod
	def setup_log(path, level = logging.DEBUG):
		l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(funcName)20s^%(lineno)04d^%(message)s'
		d_format = '%Y-%m-%d^%H:%M:%S'
		logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=level)

	def handler(self, _req):
		p = True; h = None
		_pubsub = ""
		while(p):
			try:
				if self.debug:
					_st = datetime.now()
					h = GandanMsg.recv(None, _req)
					_et = datetime.now()
					logging.info("RECV_DATA : %s" % str(h).strip())
					logging.info("RECV_TIME : %d" % ((_et-_st).seconds*1000000 + (_et-_st).microseconds))
				else:
					h = GandanMsg.recv(None, _req)

				(_cmd, _msg)	  = (h.cmd_, h.dat_)
				[_pubsub, _topic] = _cmd.split("_")
			except Exception as e:
				Gandan.error_stack()
				if str(e) in ['convert']:
					continue
				p = False
				continue

			#Note : PUB/SUB가 등록 시 경쟁하는 상황이 발생가능
			if _pubsub == "PUB": 
				try:
					if not _topic in self.pub_lock_dict.keys():
						self.pub_lock_dict[_topic] = threading.Lock()
					self.pub_lock_dict[_topic].acquire()
					if self.debug:
						_st = datetime.now()
						p = self.pub(_req, _topic, _msg)
						_et = datetime.now()
						logging.info("PUB_TIME : %d" % ((_et-_st).seconds*1000000 + (_et-_st).microseconds))
					else:
						p = self.pub(_req, _topic, _msg)
				except Exception as e:
					Gandan.error_stack()
				finally:
					self.pub_lock_dict[_topic].release()

			if _pubsub == "SUB":
				try: 
					if self.debug:
						_st = datetime.now()
						p = self.sub(_req, _topic, _msg)
						_et = datetime.now()
						logging.info("PUB_TIME : %d" % ((_et-_st).seconds*1000000 + (_et-_st).microseconds))
					else:
						p = self.sub(_req, _topic, _msg)
				except Exception as e:
					Gandan.error_stack()


		try:
			if _pubsub == "PUB":
				_req.close()
		except Exception as e:
			logging.info("#Error socket close for %s" % str(_req))

	def pub(self, _req, _topic, _msg):
		try:
			_path = self.path +_topic
			_pub = None

			#if (_topic == "ORDER" or _topic == "OM") and _req.getsockname()[0] != '127.0.0.1':
			#	_req.close()
			#	return False

			if not _topic in self.pub_topic.keys(): 
				logging.info("ADD new PUB TOPIC[%s]" % _topic)
				self.pub_topic[_topic] = []
				self.pub_topic[_topic].append(RoboMMAP(_path, _topic, self.mon, self.sz, self.isz))
				_pub = self.pub_topic[_topic][-1]
				logging.info("PUB que path : %s monitor start,r[%d]w[%d]" % (_path, _pub.r(), _pub.w()) + ", TOPIC : %s" % _topic)
			else:
				_pub = self.pub_topic[_topic][-1]

			if Gandan.version() < 3:
				_pub.writep(bytes(_msg))
			else:
				_pub.writep(bytes(_msg,'utf-8'))

			_pub.handle(False)
		except Exception as e:
			if _pub == None:
				logging.info(str(e))
				logging.info(self.pub_topic)
				return False
			else:
				Gandan.error_stack()
				logging.info("#Error During PUB[%s], " % _topic + "[%s..]" % _msg.strip()[0:50] + " r[%d]w[%d]" % (_pub.r(), _pub.w()))
				return False

		logging.info("PUB[%s], " % _topic + "^%s^%d" % (_msg.strip(), len(_msg.strip())) + " r[%d]w[%d]" % (_pub.r(), _pub.w()))
		return True

	def sub(self, _req, _topic, _msg, _type = 0):
		try:
			if _type == 0:
				if not _topic in self.sub_topic.keys():
					self.sub_topic[_topic] = []
					self.sub_topic[_topic].append(_req)
					logging.info("_topic : %s is created for SUB" % _topic)
				else:
					self.sub_topic[_topic].append(_req)
					logging.info("_topic : %s is appended for SUB" % _topic)
			else:
				if not _topic in self.sub_topic_websocket.keys():
					self.sub_topic_websocket[_topic] = []
					self.sub_topic_websocket[_topic].append(_req)
					logging.info("_topic : %s is created for SUB, websocket" % _topic)
				else:
					self.sub_topic_websocket[_topic].append(_req)
					logging.info("_topic : %s is appended for SUB, websocket" % _topic)
		except Exception as e:
			return False
		return True

	def start(self):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			logging.info("------------ MW Gandan Version[%d] Start --------------" % Gandan.version())
			s.bind(self.ip_port)
			s.listen(30)
			#Todo : 소켓 당 쓰레드를 띄우는 대신 다중 IO로 변경
			while True:
				try:
					_r, _a = s.accept()
					self.rlist.append(_r)
					t = threading.Thread(target = self.handler, args = (_r, ))
					t.start()
				except Exception as e:
					logging.info("%s"%str(e)+":%s"%str(e))
					break

	def mon(self, _topic, _data, r, w):
		logging.info("[%s]" % str(type(_data)))
		logging.info("mon data for topic[%s]" % _topic)
		if not _topic in self.sub_topic.keys() and not _topic in self.sub_topic_websocket.keys():
			logging.info("no topic for data")
			return

		error_req_list  = []
		error_req_listw = []

		#http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm
		if _topic in self.sub_topic.keys():
			for i, _req in enumerate(self.sub_topic[_topic]):
				for d in _data:
					try:
						if Gandan.version() < 3:
							GandanMsg.send(None, _req, "[%d][%d]DATA_" % (r, w) +_topic, str(d))
						else:
							GandanMsg.send(None, _req, "[%d][%d]DATA_" % (r, w) +_topic, str(d,'utf-8'))
					except Exception as e:
						error_req_list.append(_req)

			for _req in error_req_list:
				self.sub_topic[_topic].remove(_req)

		if _topic in self.sub_topic_websocket.keys():
			for i, _req in enumerate(self.sub_topic_websocket[_topic]):
				for d in _data:
					try:
						if Gandan.version() < 3:
							GandanMsg.send_websocket(None, _req, "[%d][%d]DATA_" % (r, w) +_topic, str(d))
						else:
							GandanMsg.send_websocket(None, _req, "[%d][%d]DATA_" % (r, w) +_topic, str(d,'utf-8'))
					except Exception as e:
						Gandan.error_stack()
						error_req_listw.append(_req)

		for _req in error_req_listw:
			self.sub_topic_websocket[_topic].remove(_req)

		if len(error_req_list) > 0:
			logging.info("#Error in SUB [%s] : %d request is removed" % (_topic, len(error_req_list)))

		if len(error_req_listw) > 0:
			logging.info("#Error in SUB [%s] : %d requestw is removed" % (_topic, len(error_req_listw)))

	@staticmethod
	def error_stack(stdout = False):
		_type, _value, _traceback = sys.exc_info()
		logging.info("#Error" + str(_type) + str(_value))
		for _err_str in traceback.format_tb(_traceback):
			if stdout == False:
				logging.info(_err_str)
			else:
				print(_err_str)

	@staticmethod
	def version():
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))
