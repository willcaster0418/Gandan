import socket, re, threading, logging
import hashlib, base64, json

from .Gandan    import *
from .GandanPub import *
from .GandanSub import *

class GandanWebSocket:
	def __init__(self,ip, port, sip, sport, main_mw): # _io is wating time 
		self.main_mw  = main_mw
		self.sip_port = (sip, sport)
		self.ip_port  = (ip, port)
		self.rlist    = []

	@staticmethod
	def handshake(_sock):
		request = _sock.recv(2048)
		m = re.match('[\\w\\W]+Sec-WebSocket-Key: (.+)\r\n[\\w\\W]+\r\n\r\n', str(request, 'utf-8'))
		key = m.group(1)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11' #웹소켓 고유 GUID
		 
		response  = "HTTP/1.1 101 Switching Protocols\r\n"
		response += "Upgrade: websocket\r\n"
		response += "Connection: Upgrade\r\n"
		response += "Sec-WebSocket-Accept: %s\r\n\r\n"
		r = response % str(base64.b64encode(hashlib.sha1(bytes(key,'utf-8')).digest()),'utf-8')
		_sock.send(bytes(r, 'utf-8'))

	@staticmethod
	def send(_sock, msg):
		data = bytearray(msg.encode('utf-8'))
		if len(data) > 126:
			data = bytearray([ord(b'\x81'), 126]) + bytearray(struct.pack('>H', len(data))) + data
		else:
			data = bytearray([ord(b'\x81'), len(data)]) + data
		_sock.send(data)
	 
	@staticmethod
	def recv(_sock):
		data= bytearray(_sock.recv(1))
		logging.info("ret")
		if len(data) == 0:
			return None, None
		first_byte = data[0]
		FIN = (0xFF & first_byte) >> 7
		opcode = (0x0F & first_byte)
		second_byte = bytearray(_sock.recv(1))[0]
		mask = (0xFF & second_byte) >> 7
		payload_len = (0x7F & second_byte)
		if opcode < 3:
			if (payload_len == 126):
				payload_len = struct.unpack_from('>H', bytearray(_sock.recv(2)))[0]
			elif (payload_len == 127):
				payload_len = struct.unpack_from('>Q', bytearray(_sock.recv(8)))[0]
			if mask == 1:
				masking_key = bytearray(_sock.recv(4))
			masked_data = bytearray(_sock.recv(payload_len))
			if mask == 1:
				data = [masked_data[i] ^ masking_key[i%4] for i in range(len(masked_data))]
			else:
				data = masked_data
		else:
			return opcode, bytearray(b'\x00')
		return opcode, bytearray(data)
	
	def handler(self, _sock):
		p = True
		sub_dict = {}
		while(p):
			try:
				(opcode, data) = GandanWebSocket.recv(_sock)
				if opcode == None and data == None:
					p = False
					break
				sdata = data.decode("utf-8")
				sdict = json.loads(sdata.replace("\'", "\""))
				logging.info("%s" % str(sdict))
				if sdict["type"] == "SUB":
					self.main_mw.sub(_sock, sdict["topic"], None, _type=1)
				if sdict["type"] == "PUB":
					logging.info("PUB")
					#self.main_mw.sub(_sock, sdict["topic"], None)
			except Exception as e:
				continue

		for k in sub_dict.keys():
			sub_dict[k].close()

	def start(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(self.ip_port)
		s.listen(30)
		while True:
			try:
				logging.info("ACCEPT WITH %s ... WAIT" % str(self.ip_port))
				_r, _a = s.accept()
				logging.info("ACCEPTED WITH %s ... Done" % str(self.ip_port))
				GandanWebSocket.handshake(_r)
				_r.settimeout(0.1)
				t = threading.Thread(target = self.handler, args = (_r, ))
				t.start()
			except Exception as e:
				break

