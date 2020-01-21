from lazytimer import LazyTimer
from time import time

def error(oldtime,delay):
    real_time = time()
    estimated_time = oldtime+delay
    print("============")
    print("计划 {:.3f}".format(delay))
    print("实际 {:.3f}".format(real_time-oldtime))
    print("误差 {:.3f}".format(real_time-estimated_time))

def test():
    timer = LazyTimer()
    i:int = 1
    while(i<=128):
        timer.add(time()+i,error,[time(),i])
        i*=2

if __name__=="__main__":
    test()