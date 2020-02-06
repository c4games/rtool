#coding=utf-8
import os
import os.path
import subprocess
import tempfile
import pymysql
import json
import shutil
import sqlite3
from rtool.tasks.Base import Base
from rtool.tasks.BasePostAction import output_to_temp
from rtool.tasks.BaseStatus import BaseStatus
from rtool import utils
from rtool.pcutils.md5sum_of_path import md5_for_str
from rtool.pcutils.md5sum_of_path import md5_for_file
from rtool.pcutils.md5sum_of_path import md5sum_of_path
from rtool.pcutils.md5sum_of_path import md5sum_of_dir
from rtool.pcutils.md5sum_of_path import uni_id_for_res



RC_ADDRESS = utils.getMainConfig().get("RC_ADDRESS","")
RC_ROOT = utils.getMainConfig().get("RC_ROOT","/data/home/user00/service/resource_center")
# SECRETS_FILE = "/etc/rsyncd.secrets"
# WORKER_USER = "playcrab"
logger = utils.getLogger("BaseSync")
RSYNC_TEMPLATE = "rsync -avzP $src $dst "
RSYNC_TEMPLATE_WITH_EXCLUDE = "rsync -avzP --exclude $exclude $src $dst "
MAKE_RC_DIR_TMEPLATE = "ssh $rc_address 'mkdir -p $rc_dir'"
DB_CONFIG = {
	"host":"172.16.153.49",
	"port":51000,
	"user":"tackle",
	"password":"tackle@topjoy.com",
	"db":"asset_vega"
	}
DB_CONFIG = utils.getMainConfig().get("DB_CONFIG",DB_CONFIG)

DB_CONN = None

class BaseSync(Base):
	"""与资源中心同步资源"""
	def __init__(self, options):
		super(BaseSync, self).__init__(options)
		self.options = options
		self.db_conn = DB_CONN
		self.dev_mode = self.options.get('dev',False) or self.options.get('norc',False)
		self.status = BaseStatus(options)	
		# self.table_name = "test"	
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
		if self.dev_mode:
			return
		if self.db_conn != None:
			return self.db_conn
		if not config == {}:
			try:
				conn = pymysql.connect(host=config.get("host"),user=config.get("user"),passwd=config.get("password"),db=config.get("db"),port=config.get("port"),charset="utf8")
				DB_CONN = conn
				self.db_conn = DB_CONN
				return DB_CONN
			except pymysql.Error as e:
				logger.error("Mysql Error %d: %s"%(e.args[0], e.args[1]))
				logger.error(e)
				self.status.doError()

	def reconnect(self,config):
		"""
			由于资源处理在没有缓存的情况下非常耗时，当资源数据库的数据连接时间设置过短时，会出现资源处理完成后数据库连接已经丢失，无法写入库中的情况，因此需要做客户端的断线重连
			另一方面由于get_db_conn返回的是单例的连接对象，因此重连需要提供单独的方法进行
		"""
		if self.dev_mode:
			return
		if not config == {}:
			try:
				conn = pymysql.connect(host=config.get("host"),user=config.get("user"),passwd=config.get("password"),db=config.get("db"),port=config.get("port"),charset="utf8")
				DB_CONN = conn
				self.db_conn = DB_CONN
				return DB_CONN
			except pymysql.Error as e:
				logger.error("Mysql Error %d: %s"%(e.args[0], e.args[1]))
				logger.error(e)
				self.status.doError()
		pass
	"""
	根据target建立assets_$target表

	"""
	def init_db(self):
		if self.dev_mode:
			return
		target = self.options.get('target',None)
		upgrade_path = self.options.get('upgrade_path',None)
		if target and upgrade_path:			
			remote_table_name = 'cache2_'+self.options['target'].lower()+"_"+self.options['upgrade_path']	
			create_assets_sql = ("CREATE TABLE  IF NOT EXISTS `{}`" 
								"(`asset_tag` int(32)NOT NULL, "
								"`md5` varchar(64) NOT NULL, "
								"`filename` varchar(255) NOT NULL, "
								"`url` varchar(255), "
								"`input_dir` varchar(255), "
								"`task_id` int(11) DEFAULT 0, "
								"PRIMARY KEY (`asset_tag`,`md5`,`url`,`task_id`)) default charset utf8").format('assets_'+target.lower()+"_"+upgrade_path)
			create_cache2_sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(32) NOT NULL,`cache` text,PRIMARY KEY (`res_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8 '.format(remote_table_name)
			# create_files_sql = ("CREATE TABLE  IF NOT EXISTS `{}`" 
			# 					"(`md5` varchar(64) NOT NULL, "
			# 					"`rsid` varchar(32) NOT NULL, "
			# 					"`filename` varchar(255) NOT NULL, "
			# 					"`url` varchar(255) NOT NULL, "
			# 					"PRIMARY KEY (`md5`,`url`)) default charset utf8").format('files_'+target.lower())		
			# cur.execute(create_files_sql)
			try:
				cur = self.db_conn.cursor()
				cur.execute(create_cache2_sql)
				cur.execute(create_assets_sql)
				self.db_conn.commit()				
				pass
			except Exception as e:				
				logger.error(e)
				self.db_conn.close()
				self.status.doError()
			finally:
				cur.close()
		else:
			logger.error('［错误］os_platform 或 upgrade_path 参数缺失')
			self.status.doError()

	def init_local_db(self):
		cache_root = self.options['cachedir']
		tpcache_dir = os.path.join(cache_root,'tpchache')
		if not os.path.exists(tpcache_dir):
			os.makedirs(tpcache_dir) 
		db_file = os.path.join(cache_root,'tpchache','localdb')
		sql = 'CREATE TABLE  IF NOT EXISTS `{}` (`res_id` varchar(32) NOT NULL,`cache` text,PRIMARY KEY (`res_id`))'.format('cache2')		
		try:
			conn = sqlite3.connect(db_file)
			cur = conn.cursor()			
			cur.execute(sql)
			conn.commit()
			pass
		except Exception as e:
			logger.error(e)
			self.status.doError()
		finally:
			cur.close()
			conn.close()
		pass


	def drop_table(self):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG) 
		cur = self.db_conn.cursor()
		table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
		sql = """DROP TABLE '%s'"""%(table_name)
		cur.execute(sql)
		self.db_conn.commit()
		cur.close()

	def insert_assets(self,asset_tag,md5,filename,url,input_rel_dir):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG) 
		cur = self.db_conn.cursor()
		table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
		sql = """replace %s values('%s','%s','%s','%s','%s')"""%(table_name, asset_tag,md5,filename,url,input_rel_dir)
		cur.execute(sql)
		self.db_conn.commit()
		cur.close()
		logger.debug("insert "+url+" with tag "+asset_tag+" to "+table_name)
		pass

	def insert_assets_fast(self,asset_tag,md5,filename,url,input_rel_dir):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG)
		
		try:
			cur = self.db_conn.cursor()
			table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
			sql = """replace %s values('%s','%s','%s','%s','%s')"""%(table_name, asset_tag,md5,filename,url,input_rel_dir)
			cur.execute(sql)
		except Exception as e:
			logger.error(e)
			cur.close()
			self.db_conn.close()
			self.status.doError()

		logger.debug("insert "+url+" with tag "+asset_tag+" to "+table_name)
		pass

	def insert_assets_many(self,params):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG)
		need_to_try = True
		attempt = 0
		while need_to_try and attempt<3:
			try:
				cur = self.db_conn.cursor()
				table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
				task_id = self.options.get("id",0)
				sql = """replace """+table_name+""" values(%s,%s,%s,%s,%s,"""+str(task_id)+""")"""
				cur.executemany(sql,params)
				need_to_try = False
			except Exception as e:
				logger.error(e)
				cur.close()
				# 当服务端关闭了连接以后，db_conn.close()会触发异常
				# self.db_conn.close()
				if attempt == 2:
					self.status.doError()
				else:
					self.reconnect(DB_CONFIG)					
					need_to_try = True
					attempt+=1
					logger.warning("Retry connection "+str(attempt))
			pass


		logger.debug(params)
		logger.debug("insert many to "+table_name)

	def delete_assets_with_tag(self,asset_tag):
		if self.dev_mode:
			return
		logger.debug("delete_assets_with_tag {}".format(asset_tag))
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG)
		need_to_try = True
		attempt = 0
		while need_to_try and attempt<3:
			try:
				cur = self.db_conn.cursor()
				table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
				task_id = self.options.get("id",0)
				sql = ("""UPDATE {3} SET `asset_tag`={0},`task_id`={1} WHERE `asset_tag`={2}""").format(str(-int(asset_tag)),task_id,asset_tag,table_name)				
				cur.execute(sql)
				need_to_try=False
			except Exception as e:
				logger.error(e)
				cur.close()
				# 当服务端关闭了连接以后，db_conn.close()会触发异常
				# self.db_conn.close()
				if attempt == 2:
					self.status.doError()
				else:
					self.reconnect(DB_CONFIG)					
					need_to_try = True
					attempt+=1
					logger.warning("Retry connection "+str(attempt))
			pass



	def commit_and_close_cur(self):
		try:
			self.db_conn.commit()
			cur = self.db_conn.cursor()
			cur.close()
			logger.debug("commit and close cursor")
		except Exception as e:
			logger.error(e)
			self.db_conn.close()
			self.status.doError()
			




	# def insert_files(self,md5,res_id,filename,url):
	# 	if self.dev_mode:
	# 		return
	# 	if not self.db_conn:
	# 		self.db_conn = self.get_db_conn(DB_CONFIG) 
	# 	cur = self.db_conn.cursor()
	# 	table_name = 'files_'+self.options['target'].lower()
	# 	sql = "replace %s values('%s','%s','%s','%s') "%(table_name,md5,res_id, filename ,url)
	# 	print sql
	# 	cur.execute(sql)
	# 	self.db_conn.commit()
	# 	cur.close()
	# 	pass

	# def search_assets(self,asset_tag,md5):
	# 	row = None
	# 	if self.dev_mode:
	# 		return row
	# 	cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
	# 	table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
	# 	sql = "select asset_tag, md5 from %s where asset_tag = '%s'"%(table_name, asset_tag)
	# 	#self.logger.debug(sql)
	# 	cur.execute(sql)
	# 	row = cur.fetchone()
	# 	cur.close()
	# 	if row != None:
	# 	#self.logger.debug(row)
	# 		row = json.loads(str(row[1]))
	# 	return row


	# def insert_db(self,res_id,config):
	# 	if self.dev_mode:
	# 		return
	# 	cur = self.db_conn.cursor()
	# 	sql = "insert into or replace %s values('%s','%s') "%(self.table_name, res_id, json.dumps(config))
	# 	sql = """insert into %s values('%s','%s') on duplicate key update `cache`=values(`cache`) """%(self.table_name, res_id, json.dumps(config))
	# 	cur.execute(sql)
	# 	self.db_conn.commit()
	# 	cur.close()

	# 根据传入tag查询该版本所需要所有文件 
	def search_assets_with_tag(self,asset_tag):
		rows = []
		if self.dev_mode:
			return rows
		try:
			cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
			table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
			sql = "select asset_tag, md5, filename, url, input_dir from %s where asset_tag = '%s'"%(table_name, asset_tag)
			#self.logger.debug(sql)
			cur.execute(sql)
			rows = cur.fetchall()
			cur.close()
		except Exception as e:
			logger.error(e)
			self.db_conn.close()
			self.status.doError()
		return rows
		pass

	#查询资源版本记录数量判断版本是否存在
	def search_assets_count_with_tag(self,asset_tag):
		count = 0
		if self.dev_mode:
			return count
		try:
			cur = self.db_conn.cursor()
			table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
			sql = """select count(*) from {0} where `asset_tag`={1}""".format(table_name,asset_tag)
			cur.execute(sql)			
			self.db_conn.commit()
			(count,) = cur.fetchone()
			cur.close()
		except Exception as e:
			logger.error(e)
			self.db_conn.close()
			self.status.doError()
			raise
		return count

	# def search_assets_for_single_file_with_tag(self,file_url,asset_tag):
	# 	rows = []
	# 	if self.dev_mode:
	# 		return rows
	# 	cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
	# 	table_name = 'assets_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
	# 	sql = "select count(*) from %s where asset_tag = '%s' and url = '%s'"%(table_name, asset_tag,file_url)
	# 	#self.logger.debug(sql)
	# 	cur.execute(sql)
	# 	rows = cur.fetchall()
	# 	cur.close()
	# 	return rows
	# 	pass

	# def is_file_in_assets_with_tag(self,file_url,asset_tag):
	# 	result = self.search_assets_for_single_file_with_tag(file_url,asset_tag)
	# 	count = result[0].get('count(*)',0)
	# 	if count>0:
	# 		return True
	# 	return False

	# # 根据传入rsid查询可以直接使用的文件
	# def search_files_with_rsid(self,rsid):
	# 	rows = []
	# 	if self.dev_mode:
	# 		return rows
	# 	cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
	# 	table_name = 'files_'+self.options['target'].lower()
	# 	sql = "select md5, filename, url from %s where rsid = '%s'"%(table_name, rsid)
	# 	#self.logger.debug(sql)
	# 	cur.execute(sql)
	# 	rows = cur.fetchall()
	# 	cur.close()
	# 	return rows
	# 	pass

	# 	# 根据传入rsid查询可以直接使用的文件
	# def search_files_with_md5(self,md5):
	# 	rows = []
	# 	if self.dev_mode:
	# 		return rows
	# 	cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
	# 	table_name = 'files_'+self.options['target'].lower()
	# 	sql = "select md5, filename from %s where md5 = '%s'"%(table_name, md5)
	# 	#self.logger.debug(sql)
	# 	cur.execute(sql)
	# 	rows = cur.fetchall()
	# 	cur.close()
	# 	return rows
	# 	pass

	# def search_db(self, res_md5):
	# 	row = None
	# 	if self.dev_mode:
	# 		return row
	# 	cur = self.db_conn.cursor()
	# 	#TODO 这里是否需要换库？
	# 	sql = "select res_id, cache from %s where res_id = '%s'"%(self.table_name, res_md5)
	# 	#self.logger.debug(sql)
	# 	cur.execute(sql)
	# 	row = cur.fetchone()
	# 	cur.close()
	# 	if row != None:
	# 	#self.logger.debug(row)
	# 		row = json.loads(str(row[1]))
	# 	return row

	def close_db_conn(self):
		if DB_CONN:
			DB_CONN.close()
	
	def makeRCDir(self,rc_dir):
		"""
		向rc同步资源前要保证目标目录存在，因此要先在rc上创建相应的目录
		"""
		cmd = MAKE_RC_DIR_TMEPLATE
		cmd = cmd.replace('$rc_address',RC_ADDRESS)
		cmd = cmd.replace('$rc_dir',rc_dir)
		print(cmd)
		output =""
		with tempfile.TemporaryFile() as f:
			process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE, shell=True)
			process.communicate()
			if not process.returncode==0:
				f.seek(0)
				output = f.read()
				logger.error("［错误］无法在rc上创建目录 "+output)
				self.doError()
		pass

	# def syncRC(self,config,action):
	# 	"""
	# 	将本地处理结果同步至RC及DB
	# 	"""
	# 	res_src = ""
	# 	output_uid = uni_id_for_res(config,action)
	# 	output_root = config['outputroot']
	# 	res_src = config['output-root']
	# 	if not os.path.exists(res_src):
	# 		# 尝试查找上一级目录，如果仍无法找到，则认为发生错误
	# 		res_src = os.path.split(res_src)[0]
	# 		if not os.path.exists(res_src):
	# 			logger.warning(u'［警告］SRC PATH NOT EXTISTS '+res_src)
	# 			return
	# 	dst_dir = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower())
	# 	self.makeRCDir(dst_dir)
	# 	r_dir_list = []
	# 	for item in os.listdir(res_src):
	# 		path = os.path.join(res_src,item)			
	# 		if os.path.isfile(path):
	# 			md5 = md5_for_file(path)
	# 			rc_file_name = md5
	# 			# 由于同一目录中文件过多时查找效率会大大降低，因此使用md5值的前位作为目录名存放文件
	# 			r_dir = str(md5)[0:2]
	# 			self.makeRCDir(os.path.join(dst_dir,r_dir))
	# 			dst_path = os.path.join(dst_dir,r_dir,rc_file_name)
	# 			dst_net_path = RC_ADDRESS+":"+dst_path
	# 			cmd = RSYNC_TEMPLATE
	# 			cmd = cmd.replace('$src',path)
	# 			cmd = cmd.replace('$dst',dst_net_path)
	# 			# cmd = cmd.replace('$secrets',SECRETS_FILE)
	# 			print cmd
	# 			output =""
	# 			with tempfile.TemporaryFile() as f:
	# 				process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE,shell=True)
	# 				process.communicate()
	# 				if not process.returncode==0:
	# 					f.seek(0)
	# 					output = f.read()
	# 					logger.error(u"［错误］同步出现问题 "+output)
	# 				else: 
	# 					self.syncFilesData(output_uid,os.path.join(r_dir,md5),item,os.path.relpath(path,output_root))
	# 	pass

	# def syncRCFast(self,config,action):
	# 	"""
	# 	将本地处理结果同步至RC及DB
	# 	"""
	# 	if self.dev_mode:
	# 		return
	# 	work_dir = self.options['cachedir']
	# 	work_dir_base = os.path.split(work_dir)[0]
	# 	read_to_sync_path = os.path.join(work_dir_base,'readyToSync')
	# 	res_src = ""
	# 	output_uid = uni_id_for_res(config,action)
	# 	output_root = config['outputroot']
	# 	res_src = config['output-root']
	# 	if not os.path.exists(res_src):
	# 		# 尝试查找上一级目录，因为项目组可能实现插件时不规范，改变了工作目录结构，所以做最低限度的兼容
	# 		res_src = os.path.split(res_src)[0]
	# 		if not os.path.exists(res_src):
	# 			logger.warning(u'［警告］SRC PATH NOT EXTISTS '+res_src)
	# 			return
	# 	dst_dir = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower())
	# 	# self.makeRCDir(dst_dir)
	# 	r_dir_list = []
	# 	for item in os.listdir(res_src):
	# 		path = os.path.join(res_src,item)			
	# 		if os.path.isfile(path):
	# 			md5 = md5_for_file(path)
	# 			# 由于同一目录中文件过多时查找效率会大大降低，因此使用md5值的前位作为目录名存放文件，即将文件散列到256个目录中
	# 			r_dir = str(md5)[0:2]
	# 			ready_dir = os.path.join(read_to_sync_path,r_dir)
	# 			# self.move_files_to_ready(path,ready_dir,md5)
	# 			self.syncFilesData(output_uid,os.path.join(r_dir,md5),item,os.path.relpath(path,output_root))
	# 	pass


	# def syncLocal(self,config,action):
	# 	"""
	# 	从RC取回处理资源，根据DB查询结果放置到实际需要的位置
	# 	"""
	# 	if self.dev_mode:
	# 		return
	# 	res_dst = ""
	# 	output_uid = uni_id_for_res(config,action)

	# 	output_root = config['outputroot']
	# 	data_rows = self.search_files_with_rsid(output_uid)
	# 	print "get res id as "+output_uid
	# 	print "len "+ str(len(data_rows))
	# 	print data_rows
	# 	print "======="
	# 	if len(data_rows)>0:
	# 		for row in data_rows:
	# 			md5 = row.get('md5',None)
	# 			filename = row.get('filename',None)
	# 			rel_path = row.get('url',None)
	# 			if md5 and filename:
	# 				src_path = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower(),md5)
	# 				src_rc_path = RC_ADDRESS+":"+src_path
	# 				res_dst = os.path.join(output_root,rel_path)
	# 				base_dir = os.path.split(res_dst)[0]
	# 				if not os.path.exists(base_dir):
	# 					os.makedirs(base_dir)
	# 				cmd = RSYNC_TEMPLATE
	# 				cmd = cmd.replace('$src',src_rc_path)
	# 				cmd = cmd.replace('$dst',res_dst)
	# 				# cmd = cmd.replace('$secrets',SECRETS_FILE)
	# 				print cmd
	# 				output =""
	# 				with tempfile.TemporaryFile() as f:
	# 					process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE, shell=True)
	# 					process.communicate()
	# 					if not process.returncode==0:
	# 						f.seek(0)
	# 						output = f.read()
	# 						logger.error(u"［错误］同步出现问题 "+output)
	# 						return False
	# 			else:
	# 				return False
	# 		return True
	# 	else:
	# 		return False				

	# 	pass

	# def syncFilesData(self,output_uid,md5,path,url):
	# 	self.insert_files(md5,output_uid,path,url)
	# 	pass

	def syncAssetsRc(self):
		"""
		在rtool后处理（postaction）结束后，向RC同步本次资源处理的产出，此时有两种可能
		1.在中间生成过程文件已经同步至RC，此时只需更新数据库中相应的记录
		2.在后处理中新生成了文件，这种情况需将文件同步至RC,然后再更新数据记录
		"""
		output_root = self.options['output']
		asset_tag = self.options['svn_commit']
		dst_dir = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower())
		self.makeRCDir(dst_dir)
		for parent,dirnames,filenames in os.walk(output_root):
			for filename in filenames:
				file_path = os.path.join(parent,filename)
				url = os.path.relpath(file_path,output_root)
				md5 = md5_for_file(file_path)
				r_dir = str(md5)[0:2]
				md5_path = os.path.join(r_dir,md5)
				data_rows = self.search_files_with_md5(md5_path)
				if len(data_rows)>0:
					self.insert_assets(asset_tag,md5_path,filename,url)
				else:
					res_src_file = file_path	
					self.makeRCDir(os.path.join(dst_dir,r_dir))				
					dst_path = os.path.join(dst_dir,md5_path)
					dst_net_path = RC_ADDRESS+":"+dst_path
					cmd = RSYNC_TEMPLATE
					cmd = cmd.replace('$src',res_src_file)
					cmd = cmd.replace('$dst',dst_net_path)
					# cmd = cmd.replace('$secrets',SECRETS_FILE)
					print(cmd)
					output =""
					with tempfile.TemporaryFile() as f:
						process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE,shell=True)
						process.communicate()
						if not process.returncode==0:
							f.seek(0)
							output = f.read()
							logger.error("［错误］同步出现问题 "+output)
							self.doError()
						else: 
							self.insert_assets(asset_tag,md5_path,filename,url)

	def syncReadyFilesRc(self):
		if self.dev_mode:
			return
		work_dir = self.options['cachedir']
		work_dir_base = os.path.split(work_dir)[0]
		read_to_sync_path = os.path.join(work_dir_base,'readyToSync')
		dst_dir = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower())
		dst_net_path = RC_ADDRESS+":"+dst_dir
		self.makeRCDir(dst_dir)
		cmd = RSYNC_TEMPLATE
		cmd = cmd.replace('$src',read_to_sync_path+'/')
		cmd = cmd.replace('$dst',dst_net_path+'/')
		print(cmd)
		output =""
		logger.debug(" 开始同步")
		with tempfile.TemporaryFile() as f:
			process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE,shell=True)
			process.communicate()
			if not process.returncode==0:
				f.seek(0)
				output = f.read()
				logger.error("［错误］同步出现问题 "+output)
				self.doError()
			else:
				logger.debug(" 同步完成")
		pass

	def clearReadyDir(self):
		"""
		在每次资源处理开始时清理本地同步目录，目的是防止worker上放置的资源过多
		也由于每次资源处理开始前都会清理该目录，目录不需要区分项目和target
		"""
		work_dir = self.options['cachedir']
		work_dir_base = os.path.split(work_dir)[0]
		read_to_sync_path = os.path.join(work_dir_base,'readyToSync')
		if os.path.exists(read_to_sync_path):
			shutil.rmtree(read_to_sync_path)		
		os.makedirs(read_to_sync_path)
		pass

	def syncAssetsRcFast(self):
		"""
		在rtool后处理（postaction）结束后，向RC同步本次资源处理的产出，此时有两种可能
		1.在中间生成过程文件已经同步至RC，此时只需更新数据库中相应的记录
		2.在后处理中新生成了文件，这种情况需将文件同步至RC,然后再更新数据记录
		先在建立readyToSync目录(与工作目录同级)，将本次处理产出文件按照规则放置进该目录中，然后一次rsync到rc目录中
		"""
		if self.dev_mode:
			return
		work_dir = self.options['cachedir']
		work_dir_base = os.path.split(work_dir)[0]
		read_to_sync_path = os.path.join(work_dir_base,'readyToSync')

		output_root = self.options['output']
		asset_tag = self.options['svn_commit']
		dst_dir = os.path.join(RC_ROOT,self.options['game'],self.options['target'].lower())
		self.makeRCDir(dst_dir)
		params=[]
		for parent,dirnames,filenames in os.walk(output_root):
			for filename in filenames:
				file_path = os.path.join(parent,filename)
				url = os.path.relpath(file_path,output_root)
				md5 = md5_for_file(file_path)
				r_dir = str(md5)[0:2]
				md5_path = os.path.join(r_dir,md5)
				# data_rows = self.search_files_with_md5(md5_path)
				input_rel_dir = os.path.relpath(os.path.split(file_path)[0],output_root)
				if file_path in output_to_temp:
					input_rel_dir = output_to_temp[file_path]				
				ready_dir = os.path.join(read_to_sync_path,r_dir)
				self.move_files_to_ready(file_path,ready_dir,md5)
				params.append((asset_tag,md5_path,filename,url,input_rel_dir))
				# self.insert_assets_fast(asset_tag,md5_path,filename,url,input_rel_dir)
		self.insert_assets_many(params)
		logger.debug("insert complete begin to commit")
		self.commit_and_close_cur()
		logger.debug("commit complete")
		self.syncReadyFilesRc()
		pass

	def deleteAssetsWithTag(self,asset_tag):
		"""
		删除资源版本，传入资源版本号，判断资源存在后，执行逻辑删除
		"""
		count = self.search_assets_count_with_tag(asset_tag)
		if count>0:
			self.delete_assets_with_tag(asset_tag)
			self.commit_and_close_cur()
			logger.debug("Asset {} deleted".format(asset_tag))
		else:
			logger.debug("No asset found with asset_tag {}".format(asset_tag))
			logger.debug("No need to delete assets")

	def move_files_to_ready(self,src_path,dst_dir,rename=''):
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)
		shutil.copy2(src_path,dst_dir)
		if not rename == '':
			filename = os.path.split(src_path)[1]
			ori_rn_path = os.path.join(dst_dir,filename)
			rn_path = os.path.join(dst_dir,rename)
			os.rename(ori_rn_path,rn_path) 
		pass	 

	# 将worker的本地tpcache缓存目录同步至rc
	def TPLocal2RC(self):
		if self.dev_mode:
			return
		work_dir = self.options['cachedir']
		read_to_sync_path = os.path.join(work_dir,'tpchache')
		dst_dir = os.path.join(RC_ROOT,self.options['game'],"tpchache")
		dst_net_path = RC_ADDRESS+":"+dst_dir
		cmd = RSYNC_TEMPLATE_WITH_EXCLUDE
		cmd = cmd.replace('$src',read_to_sync_path+'/')
		cmd = cmd.replace('$dst',dst_net_path+'/')
		cmd = cmd.replace('$exclude',"localdb")
		print(cmd)
		output =""
		logger.debug(" 开始同步TPcache到RC")
		with tempfile.TemporaryFile() as f:
			process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE,shell=True)
			process.communicate()
			if not process.returncode==0:
				f.seek(0)
				output = f.read()
				logger.error("［错误］同步出现问题 "+output)
				self.status.doError()
			else:
				logger.debug(" 同步完成")
		pass
	# 将rc上的缓存文件同步回本地tpcache路径
	def RC2TPLocal(self):
		if self.dev_mode:
			return
		work_dir = self.options['cachedir']
		read_to_sync_path = os.path.join(work_dir,'tpchache')
		dst_dir = os.path.join(RC_ROOT,self.options['game'],"tpchache")
		dst_net_path = RC_ADDRESS+":"+dst_dir
		self.makeRCDir(dst_dir)
		cmd = RSYNC_TEMPLATE
		cmd = cmd.replace('$src',dst_net_path+'/')
		cmd = cmd.replace('$dst',read_to_sync_path+'/')
		cmd = cmd.replace('$exclude',"localdb")
		print(cmd)
		output =""
		logger.debug(" 开始同步RC到本地TPCache")
		with tempfile.TemporaryFile() as f:
			process = subprocess.Popen(cmd,stdout=f, stderr=f, stdin=subprocess.PIPE,shell=True)
			process.communicate()
			if not process.returncode==0:
				f.seek(0)
				output = f.read()
				logger.error("［错误］同步出现问题 "+output)
				self.status.doError()
			else:
				logger.debug(" 同步完成")
		pass

	def syncCacheDataRemote(self):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG)
		logger.debug("Begin to sync local cache DB to remote")
		cur = self.db_conn.cursor() 
		cache_root = self.options['cachedir']
		db_file = os.path.join(cache_root,'tpchache','localdb')
		# print db_file
		sqlite_db_conn = sqlite3.connect(db_file)
		select_all_sql = "select * from cache2"
		remote_table_name = 'cache2_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
		insert_update_sql = """replace into """+remote_table_name+""" values(%s,%s)"""
		if sqlite_db_conn:
			sqlite_cursor = sqlite_db_conn.cursor()
			sqlite_cursor.execute(select_all_sql)
			rows = sqlite_cursor.fetchall()
			sqlite_cursor.close()
			params = []
			for row in rows:
				# das = json.loads(str(row[1]))
				das = str(row[1])
				resid = str(row[0])
				# insert_update_sql = """replace into %s values('%s','%s')"""%(remote_table_name,resid,das)
				# print insert_update_sql
				params.append((resid,das))
			try:
				cur.executemany(insert_update_sql,params)
			except Exception as e:
				logger.error(e)
				sqlite_db_conn.close()
				self.db_conn.close()
				self.status.doError()			
			sqlite_db_conn.close()
			self.db_conn.commit()
			cur.close()
		logger.debug("Finished syncing local cache DB to remote")
		pass

	def syncCacheDataLocal(self):
		if self.dev_mode:
			return
		if not self.db_conn:
			self.db_conn = self.get_db_conn(DB_CONFIG)
		logger.debug("Begin to sync cache data to local DB")
		remote_table_name = 'cache2_'+self.options['target'].lower()+"_"+self.options['upgrade_path']
		select_all_sql = """select * from %s"""%(remote_table_name)
		cur = self.db_conn.cursor() 
		cache_root = self.options['cachedir']
		db_file = os.path.join(cache_root,'tpchache','localdb')
		sqlite_db_conn = sqlite3.connect(db_file)
		if sqlite_db_conn:
			sqlite_cursor = sqlite_db_conn.cursor()	
			cur.execute(select_all_sql)		
			rows = cur.fetchall()
			cur.close()
			params=[]
			for row in rows:
				# print str(row[1])
				das = str(row[1])
				resid = str(row[0])
				params.append((resid,das))
			insert_update_sql = """replace into cache2 values(?,?)"""
			try:
				sqlite_cursor.executemany(insert_update_sql,params)
			except Exception as e:
				logger.error(e)
				sqlite_db_conn.close()
				self.db_conn.close()
				self.status.doError()
			
			sqlite_db_conn.commit()
			sqlite_cursor.close()		
			sqlite_db_conn.close()
			

		logger.debug("Finished syncing cache data to local DB")
		pass

	def syncRunDict(self):
		options={}
		options['dbconfig']=DB_CONFIG
		self.table_name = "test"
		self.db_conn = self.get_db_conn(self.options.get('dbconfig',options['dbconfig']))
		run_dict = self.options.get('run_dict',{})

		if not run_dict == {}:
			for action,config_list in list(run_dict.items()):
				for config in config_list:				
					output_id = uni_id_for_res(config)
					print(output_id)
					print(config)
					self.insert_db(output_id,config)
		pass

	def dumpData(self):
		self.db_conn = self.get_db_conn(self.options.get('dbconfig',{}))
		cur = self.db_conn.cursor()
		table_name = 'files_'+self.options['target']
		#TODO 这里是否需要换库？
		sql = "select * from %s"%(table_name)
		print(sql)
		#self.logger.debug(sql)
		cur.execute(sql)
		rows = cur.fetchall()
		cur.close()
		if rows != None:
			print(rows)


if __name__ == '__main__':
	options={}
	options['output'] = '/data/work/test/tstsync'
	options['game'] = 'demos'
	options['target'] = 'ios'
	options['upgrade_path']='__test__'
	options['cachedir']="/data/work/temp"
	options['dbconfig']={
	"host":"172.16.153.49",
	"port":51000,
	"user":"tackle",
	"password":"tackle@topjoy.com",
	"db":"test"
	}
	# DB_CONFIG = options['dbconfig']
	# print DB_CONFIG
	# # print utils.getMainConfig("DB_CONFIG")
	# # print utils.getMainConfig("RC_ADDRESS")
	# # print utils.getMainConfig("RC_ROOT")

	# # create_assets_sql = ("CREATE TABLE  IF NOT EXISTS `{}`" 
	# # 					"(`asset_tag` int(32)NOT NULL, "
	# # 					"`md5` varchar(32) NOT NULL, "
	# # 					"`filename` varchar(255) NOT NULL, "
	# # 					"`url` varchar(64)"
	# # 					"PRIMARY KEY (`asset_tag`,`md5`)) DEFAULT CHARSET=utf8").format('assets_ios')
	# # print create_assets_sql
	# # logger.debug("starting test")	
	# bs = BaseSync(options)
	# # bs.init_local_db()
	# # bs.TPLocal2RC()
	# # for i in range(1000000):
	# bs.get_db_conn(options['dbconfig'])
	# bs.init_db()
	# import time
	# # start = time.time()
	# # bs.syncCacheDataRemote()
	# # last = time.time()-start
	# # print "time "+str(last)	
	# start = time.time()
	# bs.syncCacheDataLocal()
	# last = time.time()-start
	# print "time "+str(last)
	# # bs.drop_table()

	# for j in range(0,1):
	# 	for i in range(0,10000):
	# 		try:
	# 			bs.insert_assets_fast(str(i),'xixixixixi',"somefilename","testurl","input_dir")
	# 		except Exception as e:
	# 			raise			
	# bs.commit_and_close_cur()
	# import time
	# start = time.time()
	# params=[]
	# for j in range(0,1):
	# 	for i in range(0,10000):
	# 		params.append((str(i),'xixixixixi'+str(i),"somefilename"+str(i),"testurl"+str(i),"input_dir"+str(i)))
	# try:
	# 	bs.db_conn.close()
	# 	bs.insert_assets_many(params)
	# except Exception as e:
	# 	raise
	# bs.commit_and_close_cur()
	# last = time.time()-start
	# print "use executemany() "+str(last)

	# start = time.time()
	# for j in range(0,1):
	# 	for i in range(0,10000):
	# 		try:
	# 			bs.insert_assets_fast(str(i),'xixixixixi'+str(i),"somefilename"+str(i),"testurl"+str(i),"input_dir"+str(i))
	# 		except Exception as e:
	# 			raise			
	# bs.commit_and_close_cur()
	# last = time.time()-start
	# print "use execute() "+str(last)




	# # bs.insert_assets_fast("5000",'hahahhahaha',"somefilename","testurl","input_dir")
	# # bs.commit_and_close_cur()
	# # print bs.search_assets_with_tag("5000")
	# bs.close_db_conn()
	# bs.insert_assets("50000",'hahahhahaha',"somefilename","testurl","input_dir")
	# file_path = "/Users/playcrab/Documents/demo.py"
	# ready_dir = "/Users/playcrab/Desktop/ncc"
	# rename = "hahahhaha"
	# bs.move_files_to_ready(file_path,ready_dir,rename)
	# bs.get_db_conn(options['dbconfig'])
	# his_tag = '33290'
	# file_url = 'asset/anim/wjxrxzfkimage0.plist'
	# dummy_url = 'hahahhaha'
	# for i in range(0,1000):
	# 	print bs.is_file_in_assets_with_tag(file_url,his_tag)
	# 	print bs.is_file_in_assets_with_tag(dummy_url,his_tag)
	# logger.debug("end test")
	# bs.init_db()
	# bs.insert_files(0,'test','test')
	# bs.insert_assets(0,'test','test','test')
	# print bs.search_files_with_md5('test')
 # 	print bs.search_assets_with_tag(0)
 # 	print bs.search_files_with_rsid('test')
	# bs.dumpData()
	# bs.dumpData()
	#bs.syncData()
	# bs.syncRC()			