from gandan.MMAP import *
from gandan.Gandan import *
from gandan.GandanMsg import *
from gandan.GandanPub import *
from gandan.GandanSub import *

if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8889)
		h = Gandan(l_ip_port, "./", 5000*10000, 5000)
		h.setup_log(datetime.now().strftime("./%Y%m%d")+".Gandan.log")
		h.start()

	except Exception as e:
		print("Error in Gandan", e)

