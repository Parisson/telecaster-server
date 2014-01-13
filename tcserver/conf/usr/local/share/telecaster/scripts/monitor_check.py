import sys, time, logging, socket
from threading import Thread
from logging.handlers import SMTPHandler

from watchdog.observers import Observer
from watchdog.events import *


IGNORE_PATTERNS = ['*.git/*', '*.swp', '*.swpx', '*~', '*.tmp',]
HOSTNAME = socket.gethostname()


class EmailLogger(object):
    """An email logging class"""

    def __init__(self, mailhost, fromaddr, toaddrs, subject):
        self.logger = logging.getLogger('telecaster')
        self.hdlr = SMTPHandler(mailhost, fromaddr, toaddrs, subject)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)


class ActivityEventHandler(PatternMatchingEventHandler):

    activity = True

    def on_modified(self, event):
        super(ActivityEventHandler, self).on_modified(event)
        self.activity = True


class ActivityCheck(Thread):

    def __init__(self, period, path, mailhost, fromaddr, toaddrs):
        Thread.__init__(self)
        self.period = int(period)
        self.path = path
        self.activity = False
        self.subject = 'WARNING : ' + HOSTNAME + ' : ' + 'telecaster monitor activity'
        self.logger = EmailLogger(mailhost, fromaddr, toaddrs, self.subject)
        self.event_handler = ActivityEventHandler(ignore_patterns=IGNORE_PATTERNS)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()

    def run(self):        
        while True:
            if not self.event_handler.activity:
                self.logger.logger.error('The monitor is NOT recording anymore in ' + self.path + ' ! ')
            else:
                self.event_handler.activity = False
            time.sleep(self.period)

    def stop(self):
        self.observer.stop()


if __name__ == "__main__":
    period = sys.argv[1]
    path = sys.argv[2]
    mailhost = sys.argv[3]
    fromaddr = sys.argv[4]
    toaddrs = sys.argv[5].split(',')
    check = ActivityCheck(period, path, mailhost, fromaddr, toaddrs)
    check.start()
    check.join()
