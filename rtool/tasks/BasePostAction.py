#coding=utf-8
import yaml
import logging
from rtool import utils
import click
import rtool.utils as mut
import os
import os.path
import sys
import json
import copy
import shutil
import plistlib as pl
import rtool.pcutils.md5sum_of_path as mput
from xml.etree import ElementTree
import plistlib
from rtool.tasks import BaseSync as BS
import rtool.tasks.BaseLocalChange as BLC
import rtool.tasks.BaseDecorate as BD
import rtool.tasks.BaseParseConfigs as BPC

output_to_temp = {}

logger = utils.getLogger('Task_post_action')

#Function：缓存记录上次运行结果的md5
#param：上次配置， global_cfg_dict,
#output：

def calMD5forOutputPathAndPersisted(res_root,global_cfg_dict,target,action_recorder):
    if global_cfg_dict:
        for action_type in global_cfg_dict[target]:
            configs = global_cfg_dict[target][action_type]
            for config in configs:              
                # print config['output-dir']
                md5sum = mput.md5sum_of_path(config['input'])
                if md5sum:
                    action_recorder.insert_db(md5sum+target+action_type,json.dumps(config))
                # print md5sum
                pass
            pass
        pass

    logger.debug("Begin to write config")   
    global_dict_yaml_file = open(os.path.join(res_root,"globalDict.yaml"),'w')
    global_dict_yaml_file.write(yaml.dump(global_cfg_dict))
    global_dict_yaml_file.close()
    logger.debug("finished")
pass



def relativePath(base_path,path):
    if not base_path == path:
        return path.replace(base_path+os.path.sep,'')
    else:
        return ""
    pass

#Function：拷贝生成结果到目标目录
#param：
#output：

def cacheToPublish(options):
    from rtool.tasks import BaseParseConfigs as pcfg
    logger.debug("Begin to copy resouces from cache........")
    output_dir = options['output']
    pack_cache = os.path.join(options['input'],'temp','pack',options['target'],options['game'])
    compress_cache = os.path.join(options['input'],'temp','compress',options['target'],options['game'])
    comprass_cache_root = os.path.join(options['cachedir'],'compress')
    tpcache = os.path.join(options['input'],'temp','tpcache')
    if options['cachedir']:
        tpcache = os.path.join(options['cachedir'],'tpchache')
        pack_cache = pcfg.task_settings['taskdefs']['PackupTexture']['output-root']
        compress_cache = pcfg.task_settings['taskdefs']['CompressTexture']['output-root']
        compress_cache_root = os.path.join(options['cachedir'],'compress')
    for parent,diranmes,filenames in os.walk(pack_cache):
        for filename in filenames:
            file_relative_path = relativePath(pack_cache,os.path.join(parent,filename))
            if not compress_cache_root in os.path.join(parent,filename) and not tpcache in os.path.join(parent,filename):
                relative_dir,name = os.path.split(file_relative_path)
                output_dst_dir = os.path.join(output_dir,relative_dir)
                if not os.path.exists(output_dst_dir):
                    os.makedirs(output_dst_dir)
                if not "_temp" in filename:
                    shutil.copy2(os.path.join(parent,filename),output_dst_dir)
    
    for parent,diranmes,filenames in os.walk(compress_cache):
        for filename in filenames:
            file_path = os.path.join(parent,filename)
            relv_file_path = relativePath(compress_cache,file_path)
            name,ext = os.path.splitext(relv_file_path)
            png_path = os.path.join(output_dir,name+'.png')
            plist_path = os.path.join(output_dir,name+'.plist')
            if os.path.exists(png_path):
                logger.debug("remove "+png_path)
                os.remove(png_path)

    for parent,diranmes,filenames in os.walk(compress_cache):
        for filename in filenames:
            file_relative_path = relativePath(compress_cache,os.path.join(parent,filename))
            relative_dir,name = os.path.split(file_relative_path)
            output_dst_dir = os.path.join(output_dir,relative_dir)
            if not os.path.exists(output_dst_dir):
                os.makedirs(output_dst_dir)
            if not "_temp" in filename:
                shutil.copy2(os.path.join(parent,filename),output_dst_dir)
                logger.debug("copy "+ os.path.join(parent,filename) +" to "+output_dst_dir)
    logger.debug("Finished")
    pass

"""
keep_relv_path: True(默认) 将处理完成后的工作目录中的文件复制到目标目录中，保持相对路径
                False 根据使用者传入的path_hash,将处理后的文件复制到目标目录中
path_hash: 由源目录为key，目标目录为值组成的字典,将源目录内所有文件去掉目录结构放置于目标目录中
"""
def moveToDestination(options,path_hash={},keep_relv_path = True):
    if keep_relv_path:
        cacheToPublish(options)
    else:
        if not path_hash == {}:
            for item in list(path_hash.items()):
                src_path = item[0]
                dest_path = item[1]
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                if os.path.exists(src_path):
                    for par,_,fns in os.walk(src_path):
                        for fn in fns:
                            file_path = os.path.join(par,fn)
                            shutil.copy2(file_path,dest_path)
            logger.debug("Finished")


def postProcess(options,action_recorder):
    def postProcessFunc(func):
        def record_and_copy(*args,**kargs):
            from rtool.tasks import BaseParseConfigs as pcfg
            # options=None
            # action_recorder = None
            # if kargs.has_key('options'):
            #   options = kargs['options']
            # if kargs.has_key('action_recorder'):
            #   action_recorder = kargs['action_recorder']
            if options and action_recorder:
                calMD5forOutputPathAndPersisted(pcfg.task_settings['resroot'],pcfg.global_cfg_dict,options['target'],action_recorder)
                cacheToPublish(options)
                plist_root = pcfg.task_settings['taskdefs']['PackupTexture']['output-dir']
                res_root = pcfg.task_settings['resroot']
                usage_dict = pcfg.walkAndCalImgUsage(plist_root)
                with open(os.path.join(res_root,"OverSized.yaml"),'w') as f:
                    f.write(yaml.dump(usage_dict))
            return func(*args,**kargs)
        return record_and_copy
    return postProcessFunc

def post_process(options,action_recorder):
    from rtool.tasks import parse_config_files as pcfg
    # options=None
    # action_recorder = None
    # if kargs.has_key('options'):
    #   options = kargs['options']
    # if kargs.has_key('action_recorder'):
    #   action_recorder = kargs['action_recorder']
    if options and action_recorder:
        calMD5forOutputPathAndPersisted(pcfg.task_settings['resroot'],pcfg.global_cfg_dict,options['target'],action_recorder)
        cacheToPublish(options)
        plist_root = pcfg.task_settings['taskdefs']['PackupTexture']['output-dir']
        res_root = pcfg.task_settings['resroot']
        usage_dict = pcfg.walkAndCalImgUsage(plist_root)
        with open(os.path.join(res_root,"OverSized.yaml"),'w') as f:
            f.write(yaml.dump(usage_dict))


class BasePostAction(object):
    """docstring for BasePostAction"""
    def __init__(self,options):
        super(BasePostAction, self).__init__()
        self.options = options

    def getPlistForSourceName(self,index_dict,sourceName):
        for plist in list(index_dict['indices'].keys()):
            if sourceName in index_dict['indices'][plist]['items']:
                return plist
        return None

    def relativePath(self,base_path,path):
        if not base_path == path:
            return path.replace(base_path+os.path.sep,'')
        else:
            return ""
        pass

    def makeAnimIndexFromAllPlist(self,root_path):
        logger.debug("不使用makeAnimIndexFromAllPlist")
        pass

    def processAnimIndex(self,path_attach_to_plist=""):
        logger.debug("不使用processAnimIndex")
        pass

    def completeOutputWithLsc(self):
        deleted_dir_list = BLC.DELETED_DIR_LIST
        run_dict = BPC.run_dict 
        bs = BS.BaseSync(self.options)
        bs.get_db_conn(BS.DB_CONFIG)
        # bd = BD.BaseDecorate(self.options)
        logger.debug(json.dumps(run_dict,indent=2))
        run_rel_dir_list = self.genRunDirList(run_dict)

        lsc_tag = self.options.get("last_svn_commit",'0')
        asset_tag = self.options.get('svn_commit')
        if not lsc_tag == '0':
            lsc_output_rows = bs.search_assets_with_tag(lsc_tag)
            logger.debug("search_assets_with_tag "+lsc_tag)
            params=[]
            for row in lsc_output_rows:
                md5 = row['md5']
                filename = row['filename']
                url = row['url']
                input_rel_dir = row['input_dir']
                if not self.inputDirDeleted(deleted_dir_list,input_rel_dir) and not self.inputDirReRun(run_rel_dir_list,input_rel_dir) and not self.outputUpdated(url):
                    params.append((asset_tag,md5,filename,url,input_rel_dir))
            bs.insert_assets_many(params)
            logger.debug("insert finished Begin to commit")
            bs.commit_and_close_cur()
            logger.debug("commit finished")
        pass

    def genRunDirList(self,run_dict):
        rel_dir_list = []
        for action in list(run_dict.keys()):
            for config in run_dict[action]:
                rel_dir_list.append(config['input-dir'][0])
        rel_dir_list = list(set(rel_dir_list))
        return rel_dir_list
        pass

    def inputDirDeleted(self,deleted_dir_list,input_rel_dir):
        
        input_base = self.options['input']
        input_dir = os.path.join(input_base,input_rel_dir)
        if input_dir in deleted_dir_list:
            return True
        return False
        pass

    def inputDirReRun(self,run_rel_dir_list,input_rel_dir):
        if input_rel_dir in run_rel_dir_list:
            return True
        return False
        pass

    def outputUpdated(self,url):
        output_root = self.options['output']
        possible_output_path = os.path.join(output_root,url)
        if os.path.exists(possible_output_path):
            return True
        return False
        pass

    def parseCustom(self):
        pass


    def run(self):
        plist_base = os.path.join(self.options['cachedir'],'pack',self.options['game'],self.options['target'],'anim')
        self.makeAnimIndexFromAllPlist(plist_base)
        self.processAnimIndex()
        if not self.options['dev'] and not self.options['norc']:
            self.completeOutputWithLsc()
        moveToDestination(self.options)
        pass

if __name__ == '__main__':

    options={}
    options['cachedir'] = "/data/work/temp"
    options['target'] = 'iOS'
    options['game'] = 'demos'
    plist_base = os.path.join(options['cachedir'],'pack',options['game'],options['target'])
    # bpa = BasePostAction(options)
    # bpa.makeAnimIndexFromAllPlist(plist_base)
    # calMD5forOutputPathByName('/data/work/src/dzm2/svn','/data/work/src/dzm2/svn/globalDict.yaml')
    #print mput.md5sum_of_path('/data/work/src/dzm2/svn/Resources/asset/Activity/DailySignNew')
    pass