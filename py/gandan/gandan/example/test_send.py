from gandan import MMAP
import time
from datetime import datetime as dt
m = MMAP("/tmp/some.que", 32*1024, 32)
cnt = 0
while True:
    n = dt.now().timestamp()
    m.writep(bytes(str(cnt)+"|"+str(n), 'ascii'))
    cnt += 1
    time.sleep(1)
