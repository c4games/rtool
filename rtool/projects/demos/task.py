#coding=utf-8
import yaml
import logging
from rtool import utils
import click
import rtool.utils as mut
import os
import os.path
import rtool.tasks.action_dispatch as ad
import rtool.tasks.parse_config_files as pcfg
from rtool.tasks import ActionRecorder
import rtool.pcutils.md5sum_of_path as mput
import sys
import json
import rtool.res.TPCache2 as TPCache2
import rtool.res.TPTask as TPTask
from rtool.projects.demos.extraCfg import genExtraConfigs as GEC
from rtool.projects.demos import pre_action_config_parse as prcp
from rtool.projects.demos import post_action_config_parse as pacp
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
        # tpcache 路径设置
        # tpcache = options['input']+'/temp/tpcache'
        # cache_dir = options['input']+'/temp'
        # if options['cachedir']:
        #     tpcache = options['cachedir']+'/tpchache'
        #     cache_dir = options['cachedir']
        # # 运行command actions
        # pcfg.run_command_actions(options['target'])
        # # 分派配置项，执行action 
        # self.action_recorder =ActionRecorder.ActionRecorder(tpcache)  
        # if not options["imgincsd"] and not options["clean"]:
        #     if pcfg.global_cfg_dict and pcfg.task_settings:
        #         action_run_order = pcfg.task_settings['runorder']
        #         if options["actionname"]:
        #             action_run_order = options['actionname'].split(',')
        #         for action_type in action_run_order:
        #             print "=======================================> "+action_type
        #             config = pcfg.global_cfg_dict[options['target']][action_type]             
        #             action_module = pcfg.getActionModuleByType(action_type)
        #             plugin_dir = pcfg.getPluginDir()
        #             if action_module and plugin_dir:
        #                 for option in config:
        #                     logger.debug("execAction =======> "+option['output-dir'])
        #                     if pcfg.isToGo(option,options['target'],action_type,self.action_recorder):
        #                         option['cachedir'] = cache_dir 
        #                         ad.invokeClean("tp_task",action_module,plugin_dir,option)
        #                         ad.invokeAction("tp_task",action_module,plugin_dir,option,tpcache)
        # # 单独清理资源的操作
        # if options['clean']:
        #     for action_type in pcfg.global_cfg_dict[options['target']]:
        #         config = pcfg.global_cfg_dict[options['target']][action_type]             
        #         action_module = pcfg.getActionModuleByType(action_type)
        #         plugin_dir = pcfg.getPluginDir()
        #         if action_module and plugin_dir:
        #             for option in config:                        
        #                 ad.invokeClean("tp_task",action_module,plugin_dir,option)
        bpc = BaseParseConfigs(options)
        bpc.run()
               
        return True
  
    def preAction(self,options):
        if options['target'] == 'ios':
            options['target'] = 'iOS'
        if options['target'] == 'android':
            options['target'] = 'Android'
        # prcp.dec_options = options
        # print prcp.dec_options
        # preActionParse = prcp.PresActionConfigParse(options)
        # print "PresActionConfigParse init"        
        # return preActionParse.go()

    def postAction(self,options):
        bpa = BasePostAction(options)
        bpa.run()
        pass	
    	# postActionParse = pacp.PostActionConfigParse(options,self.action_recorder)    	
     #    return postActionParse.go()


