from gandan.MMAP import *
from gandan.GandanWebSocket import *
from gandan.GandanMsg import *
from gandan.GandanPub import *
from gandan.GandanSub import *
if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8080)
		h = GandanWebSocket(l_ip_port[0], l_ip_port[1], None)
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

