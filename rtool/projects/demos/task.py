#coding=utf-8
import yaml
import logging
from rtool import utils
import click
import rtool.utils as mut
import os
import os.path
import rtool.pcutils.md5sum_of_path as mput
import sys
import json
import rtool.res.TPCache2 as TPCache2
import rtool.res.TPTask as TPTask
from rtool.tasks.task import AbstractTask
from rtool.tasks import BasePreAction
from rtool.tasks.BaseParseConfigs import BaseParseConfigs
from rtool.tasks.BasePostAction import BasePostAction

logger = utils.getLogger('DemosTask')

def getInstance(task_context):
    return DemosTask(task_context)

class DemosTask(AbstractTask):
    """DemosTask"""
    action_recorder = None
    def __init__(self,ctx):
        super( DemosTask, self).__init__(ctx)
        pass        
    def rumCommand(self,cmd,options):
        pass
    def execAction(self, options):
        bpc = BaseParseConfigs(options)
        bpc.run()
               
        return True
  
    def preAction(self,options):
        if options['target'] == 'ios':
            options['target'] = 'iOS'
        if options['target'] == 'android':
            options['target'] = 'Android'


    def postAction(self,options):
        bpa = BasePostAction(options)
        bpa.run()
        pass	


