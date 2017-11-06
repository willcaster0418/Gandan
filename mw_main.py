from MW.MMAP import *
from MW.Gandan import *
from MW.GandanMsg import *
from MW.GandanPub import *
from MW.GandanSub import *

if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8889)
		h = Gandan(l_ip_port, "/home/gandan/que/", 10000, 500)
		h.setup_log(datetime.now().strftime("/home/gandan/log/%Y%m%d")+".Gandan.log")
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

