# fcntl.py — заглушка для Windows
def fcntl(fd, op, arg=0):
    return 0

def flock(fd, op):
    return

def ioctl(fd, op, arg=0, mutable_flag=True):
    if mutable_flag:
        return 0
    return b""

def lockf(fd, operation, length=0, start=0, whence=0):
    return

LOCK_SH = 1
LOCK_EX = 2
LOCK_NB = 4
LOCK_UN = 8