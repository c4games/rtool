#coding=utf8
import os
import sys
import plistlib
import json
import hashlib
import shutil
import argparse
import pymysql
import logging
import subprocess
import sqlite3
from os.path import getsize
from .pcutils.md5sum_of_path import md5_for_file
from .pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json
from .pcutils.expand_path_template_to_real_pathes import expand_path_template_to_pathes

class TPCache2():

    def __init__(self, cache_dir, mysql=None):
        self.logger = logging.getLogger(__name__)
        self.is_server = (mysql != None)
        self.db_conn = None
        self.cache_dir = cache_dir

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.table_name = 'cache2'
        if self.is_server:
            self.db_conn = self.get_db_conn(mysql)
        else:
            local_db = os.path.join(self.cache_dir, 'localdb')
            self.db_conn = sqlite3.connect(local_db)
            self.init_db()



    """
    获取数据库连接
    @params config
    {
    "host":"127.0.0.1"
    ,"port":3006
    ,"user":"cody"
    ,"password":"cody"
    ,"db":"db_name"
    }
    """
    def get_db_conn(self, config):
        if self.db_conn != None:
            return self.db_conn

        try:
            conn = pymysql.connect(host=config.get("host"),user=config.get("user"),passwd=config.get("password"),db=config.get("db"),port=config.get("port"),charset="utf8")
            self.db_conn = conn
            return conn
        except pymysql.Error as e:
             raise Exception("Mysql Error %d: %s"%(e.args[0], e.args[1]))
            
    """
    创建数据库
    """
    def init_db(self):
        cur = self.db_conn.cursor()
#        cur.execute('create database if not exists tp_cache')
        sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(32) NOT NULL,`cache` text,PRIMARY KEY (`res_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8 '.format(self.table_name)
        if not self.is_server:
            sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(32) NOT NULL,`cache` text,PRIMARY KEY (`res_id`))'.format(self.table_name)
        cur.execute(sql)
        self.db_conn.commit()
        cur.close()


    """
    根据res_id 查表并返回查询到的记录
    @params res_md5 资源加密后的唯一id
    return 
    {"datas": ["cdf35c18e622bd0e661e886642b1d640.plist"], "sheets": ["eb334b75805fb68962ff84c59d41ecef.pvr"]}
    """
    def search_db(self, res_md5):
        cur = self.db_conn.cursor()
        #TODO 这里是否需要换库？
        sql = "select res_id, cache from %s where res_id = '%s'"%(self.table_name, res_md5)
        #self.logger.debug(sql)
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        if row != None:
            #self.logger.debug(row)
            row = json.loads(str(row[1]))
        return row


    """
    保存已经处理过的资源数据
    @params res_md5 资源加密后的唯一id
    @params cache 缓存数据
    {"datas": ["cdf35c18e622bd0e661e886642b1d640.plist"], "sheets": ["eb334b75805fb68962ff84c59d41ecef.pvr"]}
    """
    def insert_db(self, res_md5, cache):
        cur = self.db_conn.cursor()
        sql = "insert into %s values('%s','%s') "%(self.table_name, res_md5, json.dumps(cache))
        # TODO 代码稳定之后，应该用上面的sql
        sql = """insert into %s values('%s','%s') on duplicate key update `cache`=values(`cache`) """%(self.table_name, res_md5, json.dumps(cache))
        if not self.is_server:
            sql = """insert or replace into %s values('%s','%s') """%(self.table_name, res_md5, json.dumps(cache))
        cur.execute(sql)
        self.db_conn.commit()
        cur.close()

    """
    把处理好的文件存入缓存中，并返回缓存的资源信息
    @params files 经过TP处理后的sheet文件 或 data文件(绝对路径)
    ['xxmd5.pvr','yyymd5.pvr'](只有文件名)
    """
    def save_files_to_cache_dir(self,files):
        cached_filenames = []
        for f in files:
            # 实际不同工具生成文件的数量不同，因此可能出现预计的文件没有产出的情况，这种情况直接跳过即可
            if not os.path.exists(f):
                continue
            suffix = os.path.splitext(f)[1]
            f2 = md5_for_file(f) + suffix
            dirname = f2[0:2]
            copy_dir = os.path.join(self.cache_dir,dirname)
            if not os.path.exists(copy_dir):
                os.makedirs(copy_dir) 
            self.logger.debug("save to cache %s => %s"%(f, f2))
            shutil.copy(f, os.path.join(copy_dir, f2))
            rename = dirname+'/'+f2
            cached_filenames.append(rename)
        return cached_filenames


    def run_command_without_cache(self,task):
        output =  task.run()
        if output == False:
            return False
        cache_info = {}

        sheet_files = task.get_ouput_sheet_files()
        data_files = task.get_ouput_data_files()

        cache_info['sheets'] = self.save_files_to_cache_dir(sheet_files)
        cache_info['datas'] = self.save_files_to_cache_dir(data_files)

        res_md5 = task.get_task_id()
        self.insert_db(res_md5, cache_info)

    def run_command_with_cache(self,task,cache_info):
        d = list(cache_info['datas'])
        d.extend(cache_info['sheets'])
        is_cache_exist = True
        for f in d:
            cache_file = os.path.join(self.cache_dir,f)
            #部分异常情况下存储的cache文件为空
            #2015-07-01 cody
            if not os.path.exists(cache_file) or (getsize(cache_file) == 0):
                is_cache_exist = False
                break

        if not is_cache_exist :
            self.run_command_without_cache(task)

        data_files = expand_path_template_to_pathes(task.data_file,len(cache_info['datas']))
        for i in range(len(cache_info['datas'])):
            cache_file = os.path.join(self.cache_dir,cache_info['datas'][i])
            data_file = data_files[i]
            # self.logger.debug("copy from cache %s => %s"%(cache_file, data_file))
            dirname,filename = os.path.split(data_file)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copy(cache_file, data_file)

        sheet_files = expand_path_template_to_pathes(task.sheet_file,len(cache_info['sheets']))
        for i in range(len(cache_info['sheets'])):
            cache_file = os.path.join(self.cache_dir,cache_info['sheets'][i])
            sheet_file = sheet_files[i]
            # self.logger.debug("copy from cache %s => %s"%(cache_file, sheet_file))
            dirname,filename = os.path.split(sheet_file)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copy(cache_file, sheet_file)

    def run_task(self,task):
        res_md5 = task.get_task_id()
        if res_md5 == None:
            # 输入目录为空，直接跳过
            return

        #multiple_output = (sheet_path.find('{n}') != -1 or data_path.find('{n}') != -1)
        cache_info = self.search_db(res_md5)
        if cache_info == None:
            self.run_command_without_cache(task)
        else:
            self.run_command_with_cache(task,cache_info)

    """
    这里需要筛选出哪些command需要做tp 哪些直接cp文件
    @params command_array
    """
    def command_arrange(self, tp_tasks):
        #self.init_db(db_conn) #提前创建好
        for task in tp_tasks: 
            self.run_task(task)
        if self.db_conn != None: 
            self.db_conn.close()

    """
    返回cachedir
    """
    def get_cache_dir(self):
        return self.cache_dir

if __name__ == '__main__':
    from .TPTask import TPTask
    tp = '/data/work/demos/rtool/temp/demos/cache/task/pack/asset/tpcache'
    tp_command="Texturepacker --sheet /data/work/demos/rtool/temp/demos/cache/task/pack/asset/anim/anniudonghuaimage{n}.png --data /data/work/demos/rtool/temp/demos/cache/task/pack/asset/anim/anniudonghuaimage{n}.plist --opt RGBA8888 --multipack  --format cocos2d --scale 1 /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_01_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_blue_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_blueBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_green_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_greenBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_light02_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_light03_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_sjg_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_yellow_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardA_yellowBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_blue_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_blue_turn_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_blueBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_green_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_GreenBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_yellow_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardB_YellowBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_blue_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_buleBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_green_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_GreenBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_yellow_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/CardC_yellowBG_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg01_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg02_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg03_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg04_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg05_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg06_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg07_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg08_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg09_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg10_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg11_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/hg12_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg01_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg02_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg03_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg04_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg05_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg06_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg07_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg08_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg09_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg10_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg11_anniudonghuaimage.png /data/work/demos/vegasvn/frontend/Assets/anim/flash_bak/Z_战斗动画/A_按钮动画/anniudonghuaimage/kg12_anniudonghuaimage.png --border-padding 2 --shape-padding 2"
    tp_cache = TPCache2(tp)
    tp_cache.command_arrange([TPTask.task_from_command(tp_command.split())])
    # command_array = [
    #         ['/usr/local/bin/TexturePacker', '--max-size','512','--multipack','--format', 'cocos2d',  '--sheet', '/data/work/tp_test/code_data/a{n}.png', '--data', '/data/work/tp_test/code_data/a{n}.plist', '/data/work/walle/kof/asset/Assets/anim/人物动画/草薙京/dashezhiimage'],
    #         #['/usr/local/bin/TexturePacker', '--format', 'cocos2d',  '--sheet', '/data/work/tp_test/code_data/1.png', '--data', '/data/work/tp_test/code_data/1.plist', '/data/work/walle/package/kof/tmp/fakefrontend/svn/Assets/anim/人物动画/草薙京/dashezhiimage'],
    #         ]
    # mysql = {"host":"192.168.0.18","port":3306,"user":"playcrab","password":"airmud","db":"tp_cache"}
    # cache_dir = "/data/work/walle/package/kof/tpcachebak/"
    # tasks = []
    # for c in command_array:
    #     tasks.append(TPTask.task_from_command(c))
    # tp = TPCache2(cache_dir, mysql)
    # tp.command_arrange(tasks)

