from time import sleep,time
from queue import PriorityQueue
from threading import Thread

class LazyItem:
    # function(p1,p2,...)
    # args = [p1,p2,...]
    def __init__(self,timestamp,function,args):
        self.timestamp = timestamp
        self.__function = function
        self.__args = args

    def run(self):
        self.__function(*self.__args)

    def __lt__(self,other):
        return self.timestamp<other.timestamp

class LazyTimer:
    ONE_SECOND = 1
    ONE_MINUTE = ONE_SECOND * 60
    ORIGINAL_SLEEP_TIME = 0.001
    
    def __init__(self):
        self.__reset_sleep_time()
        self.priority_queue = PriorityQueue()
        Thread(target=self.__background_check_and_run).start()

    def __sleep_for_a_while(self):
        sleep(self.__sleep_time)
        if self.__sleep_time < LazyTimer.ONE_SECOND:
            self.__sleep_time *= 2
        elif self.__sleep_time < LazyTimer.ONE_MINUTE:
            self.__sleep_time += LazyTimer.ONE_SECOND
    
    def __nothing_to_do(self):
        if self.priority_queue.empty(): return True
        item:LazyItem = self.priority_queue.queue[0]
        return item.timestamp > time()

    def __background_check_and_run(self):
        while(True):
            if(self.__nothing_to_do()):
                self.__sleep_for_a_while()
            else:
                item:LazyItem = self.priority_queue.get()
                item.run()


    def __reset_sleep_time(self):
        self.__sleep_time = LazyTimer.ORIGINAL_SLEEP_TIME

    def __add(self,item:LazyItem):
        self.priority_queue.put(item)
        self.__reset_sleep_time()

    def add(self,timestamp,function,args):
        item = LazyItem(timestamp,function,args)
        self.__add(item)


