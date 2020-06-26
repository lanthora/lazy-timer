from queue import PriorityQueue
from threading import Thread
from time import sleep, time


class LazyItem:
    # function(p1,p2,...)
    # args = [p1,p2,...]
    def __init__(self, timestamp, function, args):
        self.timestamp = timestamp
        self.__function = function
        self.__args = args

    def run(self):
        if(len(self.__args) == 0):
            self.__function()
        else:
            self.__function(*self.__args)

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class LazyTimer:
    ONE_SECOND = 1
    ONE_MINUTE = ONE_SECOND * 60

    def __init__(self):
        self.priority_queue = PriorityQueue()
        Thread(target=self.__background_check_and_run).start()

    def __sleep_for_a_while(self):
        sleep(LazyTimer.ONE_MINUTE)

    def __nothing_to_do(self):
        if self.priority_queue.empty():
            return True
        item: LazyItem = self.priority_queue.queue[0]
        return item.timestamp > time()

    def __background_check_and_run(self):
        while(True):
            if(self.__nothing_to_do()):
                self.__sleep_for_a_while()
            else:
                item: LazyItem = self.priority_queue.get()
                item.run()

    def __add(self, item: LazyItem):
        self.priority_queue.put(item)

    def add(self, timestamp, function, args: dict = []):
        item = LazyItem(timestamp, function, args)
        self.__add(item)


if __name__ == "__main__":
    def test(msg="Hello World"):
        print(msg)

    lt = LazyTimer()
    lt.add(time(), test)
    lt.add(time()+3, test, [])
    lt.add(time()+6, test, ["test"])
