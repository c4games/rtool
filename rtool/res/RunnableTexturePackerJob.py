#coding=utf8

from . import MultiProcessRunner
import logging
import threading
from . import TPCache2
import subprocess
import os
from ..utils import is_true
from ..utils import getLogger

from ..pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json
from ..pcutils.expand_path_template_to_real_pathes import expand_path_template_to_real_pathes

class RunnableTexturePackerJob(MultiProcessRunner.JobInterface):
    def __init__(self,task,tp_cache_dir):
        self.finished = False
        self.started = False
        self.task = task 
        self.success = False
        self.output = ''
        self.tp_cache_dir = tp_cache_dir

    def start(self):
        """启动任务"""
        #t = threading.Thread(target=self.run, args=(local_data,))
        self.t = threading.Thread(target=self.run)
        self.t.start()
        self.started = True

    def run(self):
        logger = getLogger('RunnableTexturePackerJob')
        try:
            # 2015-11-02 21:02:03 开发阶段也使用 TPCache，TPCache不再支持mysql
            tp = TPCache2.TPCache2(self.tp_cache_dir)
            tp.command_arrange([self.task])
            self.output = 'output'
            
            self.run_filters(self.task.filters,self.task.data_file,self.task.sheet_file)

            self.finished = True
            self.success = True

        except Exception as ex:
            logger.debug('failed RunnableTexturePackerJob')
            logger.exception(ex)
            self.output = ''
            self.finished = True
            self.success = False

    def run_filters(self,filters,data_path,sheet_path):
        logger = logging.getLogger(__name__)
        if filters == None:
            return
        import tpfilter
        data_paths = expand_path_template_to_real_pathes(data_path)
        sheet_paths = expand_path_template_to_real_pathes(sheet_path)
        if len(data_paths) != len(sheet_paths):
            raise Exception("file count not match\n"
                            "{} has {} files and {} has {} files"
                            .format(data_path,len(data_paths),
                                    sheet_path,len(sheet_paths)))
        for i in range(len(data_paths)):
            data_path = data_paths[i]
            sheet_path = sheet_paths[i]
            for filter_name in filters:
                abc = tpfilter.TPFilterFactory.getFilter(filter_name)
                logger.debug("run filter [{}] for [{}][{}]"
                             .format(filter_name,data_path,sheet_path))
                print(abc.run(data_path, sheet_path))

    def isFinished(self):
        """检查任务是否结束"""
        #return not self.t.is_alive()
        return self.finished

    def isSucceeded(self):
        """当任务结束后，检查任务是否执行成功"""
        return self.success

    def getOutput(self):
        """当任务结束后，返回任务的输出"""
        return self.output

    def __str__(self):
        return str(self.task)

if __name__ == '__main__':
    args = ['/usr/local/bin/TexturePacker', '--format', 'cocos2d', '--opt', 'PVRTC2', '--sheet', '/tmp/1.pvr', '--data', '/tmp/1.plist', '/tmp/abc']
    cache_dir = "/data/work/walle/package/kof/tpcache/"
    jobs = MultiProcessRunner.JobList()
    jobs.append(RunnableTexturePackerJob(args,cache_dir))
    failed_jobs = jobs.run()
