
import logging


from rtool import utils
from rtool.base.BaseClass import BaseClass
from rtool.base.ProgressLogger import ProgressLogger

class RtoolJob(BaseClass):

    def __init__(self, options):
        BaseClass.__init__(self, options)
        self._job_name = 'base'

    def _run_tasks(self, job_record):
        pass

    def _finish_job(self):
        pass


    @property
    def logger(self):
       return ProgressLogger()
        # return utils.getLogger(self._job_name)

    def run(self):
        """"""
        print('run RtoolJob')
        pass



if __name__ == '__main__':
    bar = Bar()

    test = list(range(0,100))

    bar.iter(test)

