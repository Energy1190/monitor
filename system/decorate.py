import threading
from classes.vals import Count

def counter(class_name, operation):
    def class_count(func):
        def wraper(*args, **kwargs):
            x = Count()
            x.set_count(class_name, operation)
            return func(*args, **kwargs)
        return wraper()

def maintenance(time):
    def main_func(func):
        def wraper(*args, **kwargs):
            threading.Thread(target=flush_counts,args=(time)).start()
            return func(*args, **kwargs)
        return wraper()

def flush_counts(time):
    while True:
        x = Count()
        x.update_base()
        time.sleep(time)
