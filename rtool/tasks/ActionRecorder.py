#coding=utf8
import os
import os.path
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

"""
在资源处理的postAction中纪录本次处理中资源对应的配置信息，下次处理时查询比对，如果配置信息一致则直接使用上次的处理结果
"""
class ActionRecorder():

    def __init__(self, cache_dir, mysql=None):
        self.logger = logging.getLogger(__name__)
        self.is_server = (mysql != None)
        self.db_conn = None
        self.cache_dir = cache_dir

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.table_name = 'action_record'
        if self.is_server:
            self.db_conn = self.get_db_conn(mysql)
        else:
            local_db = os.path.join(self.cache_dir, 'action_db')
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
        sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(64) NOT NULL,`cache` text,PRIMARY KEY (`res_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8 '.format(self.table_name)
        if not self.is_server:
            sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(64) NOT NULL,`cache` text,PRIMARY KEY (`res_id`))'.format(self.table_name)
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

    def dump_db(self):
    	cur = self.db_conn.cursor()
    	#TODO 这里是否需要换库？
    	sql = "select * from %s"%(self.table_name)
    	#self.logger.debug(sql)
    	cur.execute(sql)
    	rows = cur.fetchall()
    	cur.close()
    	print(rows)
    	

if __name__ == '__main__':
	action_record = ActionRecorder('/data/work/src/dzm2/svn/temp/tpcache')
	action_record.dump_db()







