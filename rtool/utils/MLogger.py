import logging
from rtool.base.Singleton import Singleton
from rtool.utils.ColorizingStreamHandler import ColorizingStreamHandler
from rtool.utils.progress.bar import (
    Bar, ChargingBar, FillingCirclesBar, FillingSquaresBar, IncrementalBar,
    ShadyBar,
)

class BlueEmojiBar(IncrementalBar):

    suffix = "%(percent)d%%"
    bar_prefix = " "
    bar_suffix = " "
    phases = (u"\U0001F539", u"\U0001F537", u"\U0001F535")  # type: Any

class FUBar (FillingSquaresBar):
    empty_fill = "U"
    fill = "F"

MLOGGER_COLOR = 0
MLOGGER_PROGRESS = 1
MLOGGER_COLOR_PROGRESS = 2

class MLogger():
    """docstring for MLogger"""

    def __init__(self,name='',logger_type=MLOGGER_COLOR_PROGRESS, *args, **kwargs):
        super(MLogger, self).__init__()
        self.bar = None
        self.log = None
        self.suffix = '%(index)d/%(max)d - %(percent).1f%% - 预计 %(eta)ds 后完成'
        self.log = logging.getLogger(name)

        for handler in  self.log.handlers[:]:
            self.log.removeHandler(handler)

        if logger_type == MLOGGER_COLOR or logger_type == MLOGGER_COLOR_PROGRESS:
            console = ColorizingStreamHandler()
            console.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console.setFormatter(formatter)

            self.log.setLevel(logging.DEBUG)
            self.log.addHandler(console)

        if logger_type == MLOGGER_PROGRESS or logger_type == MLOGGER_COLOR_PROGRESS:
            self.bar = IncrementalBar(suffix=self.suffix, *args, **kwargs)

    def getLogger(self):            
        return self
        pass

    def setLevel(self,level):
        self.log.setLevel(level)

    def debug(self, s, *args, **kwargs): 
        self.log.debug(s,*args,**kwargs)

    def info(self, s, *args, **kwargs):
        self.log.info(s,*args,**kwargs)

    def warning(self, s, *args, **kwargs):
        self.log.warning(s,*args,**kwargs)

    def error(self, s, *args, **kwargs):
        self.log.error(s,*args,**kwargs)

    def critical(self, s, *args, **kwargs):
        self.log.critical(s,*args,**kwargs)

    def reset(self):
        if self.bar:
            self.bar.goto(0)

    def next(self):
        if self.bar:
            self.bar.next()

    def finish(self):
        if self.bar:
            self.bar.finish()

    def setProcessBar(self,bar):
        if bar:
            self.bar = bar

if __name__ == '__main__':
    # bar = Bar(suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
    bar = MLogger("MLogger",max=68)
    test = range(0,68)
    print(bar)
    bar.debug("Test test test")

    import time
    for t in test:
        time.sleep(.02) # Do some work
        bar.next()
    bar.finish()
    bar.setProcessBar(FUBar(suffix=bar.suffix,max=68))
    # bar.goto(0)
    bar.reset()
    for t in test:
        time.sleep(.03)
        bar.next()
    bar.finish()
    bar = MLogger("END MLogger")
    bar.reset()
    for t in test:
        time.sleep(.01)
        bar.next()
    bar.finish()
    bar.warning("FIN")
    bar.critical("Have A Nice Day")
    log = MLogger("SoloLogger")
    print(log)
    log.info("Hello Again")





        
