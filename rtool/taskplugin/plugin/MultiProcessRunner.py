#coding=utf-8
import shutil
import os
import sys
import re
# import logging
import subprocess
import plistlib
import pprint
import time
import json
import tempfile
import rtool.utils as utils

# def create_logger(name):
#     # create logger with 'spam_application'
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)
#     # create file handler which logs even debug messages
#     fh = logging.FileHandler(name+'.log')
#     fh.setLevel(logging.DEBUG)
#     # create console handler with a higher log level
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#     # create formatter and add it to the handlers
#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#     fh.setFormatter(formatter)
#     ch.setFormatter(formatter)
#     # add the handlers to the logger
#     logger.addHandler(fh)
#     logger.addHandler(ch)
#     return logger

class JobInterface(object):
    """定义一个可执行的任务"""

    def __init__(self):
        self.finished = False
        self.started = False

    def start(self):
        """启动任务"""
        raise NotImplementedError( "Should have implemented this")

    def isFinished(self):
        """检查任务是否结束"""
        raise NotImplementedError( "Should have implemented this")

    def isSucceeded(self):
        """当任务结束后，检查任务是否执行成功"""
        raise NotImplementedError( "Should have implemented this")

    def getOutput(self):
        """当任务结束后，返回任务的输出"""
        raise NotImplementedError( "Should have implemented this")

    def __str__(self):
        raise NotImplementedError( "Should have implemented this")

class RunnableShellCommandJob(JobInterface):
    def __init__(self,args):
        JobInterface.__init__(self)
        self.args = args
        self.stdout = None
        self.process = None
        self.returncode = None
        self.output = None

    def start(self):
        self.stdout = f = tempfile.TemporaryFile()
        self.process = subprocess.Popen(self.args,stdout=f, stderr=f, stdin=subprocess.PIPE)
        self.started = True

    def isFinished(self):
        if not self.started:
            return False
        if not self.finished:
            self.returncode = self.process.poll()
            if self.returncode == None:
                return False

            self.finished = True
            self.stdout.seek(0)
            self.output = self.stdout.read()
            self.stdout.close()

        return True

    def isSucceeded(self):
        return self.returncode == 0

    def getOutput(self):
        return self.output

    def __str__(self):
        return ' '.join(self.args)


class MultiProcessRunner():
    """用多进程执行任务的类

        Usage:

            mpr = MultiProcessRunner(process_count=8)
            jobs = [RunnableShellCommandJob(['ls','/']),RunnableShellCommandJob(['ls','/Users'])]
            failed_jobs = mpr.run_jobs(jobs)
            for job in failed_jobs:
                print job.getOutput()
    """

    def __init__(self,process_count=8):
        """初始化，通过process_count 参数指定最多使用的进程数量"""
        self.process_count = process_count
        self.disable_print = os.environ.get('disable_print','0')
        self.process_info = {}
        #self.logger = create_logger('MultiProcessRunner')
        self.logger = utils.getLogger('RES')

    def check_jobs(self,process_arr):
        """检查正在执行的jobs，找出未执行完毕的jobs和执行失败的jobs"""
        unfinished_process_arr = []
        failed_process_arr = []
        for job in process_arr:
            if job.isFinished():
                if not job.isSucceeded():
                    failed_process_arr.append(job)
            else:
                unfinished_process_arr.append(job)
        return unfinished_process_arr,failed_process_arr


    def run_jobs(self,jobs):
        """执行 jobs(JobInterface类)，返回 执行失败的jobs数组"""
        # self.logger.info('start tp jobs')
        process_arr = []
        all_failed_process_arr = []
        job_total_count = len(jobs)
        while len(jobs) > 0 or len(process_arr) > 0:
            job_remain_count = len(jobs)
            job_running_count = len(process_arr)
            job_failed_count = len(all_failed_process_arr)
            if job_remain_count > 0 and job_running_count < self.process_count:
                job = jobs.pop()
                if self.disable_print != '1':
                    self.logger.debug('total jobs %d , %d jobs remain, %d running, %d failed'%(job_total_count,job_remain_count,job_running_count,job_failed_count))
                    self.logger.debug('start job %s'%(job))
                job.start()
                process_arr.append(job)

            unfinished_process_arr,failed_process_arr = self.check_jobs(process_arr)
            all_failed_process_arr.extend(failed_process_arr)
            process_arr = unfinished_process_arr
            #pprint.pprint(process_arr)
            time.sleep(0.05)

        self.logger.info('finish tp jobs')
        return all_failed_process_arr


class JobList(list):
    def __init__(self):
        list.__init__(self)

    def show(self):
        for i in self:
            print(i)

    def run(self,process_count = None):
        if process_count == None:
            import multiprocessing
            process_count = multiprocessing.cpu_count()
        mpr = MultiProcessRunner(process_count=process_count)
        failed_jobs = mpr.run_jobs(self)
        return failed_jobs
