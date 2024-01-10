from gandan.MMAP import *
from gandan.Gandan import *
from gandan.GandanMsg import *
from gandan.GandanPub import *
from gandan.GandanSub import *
if __name__ == "__main__":
	try:
		l_ip_port = ("0.0.0.0", 8889)
		mw = Gandan(l_ip_port, "/dev/shm", 50*100, 50)
		#mw.setup_log(datetime.datetime.now().strftime("./%Y%m%d")+".Gandan.log")
		mw.start()
	except Exception as e:
		print("Error in Gandan", e)

