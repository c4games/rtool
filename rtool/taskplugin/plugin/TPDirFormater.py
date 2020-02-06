#coding=utf-8
import os
import os.path
import shutil
import sqlite3
import json

def format_tp_dir(cache_root):
	filenames = os.listdir(cache_root)
	for filename in filenames:
		if not "localdb" in filename and not os.path.isdir(os.path.join(cache_root,filename)):
			name,ext = os.path.splitext(filename)
			dir_name = name[0:2]
			dir_path = os.path.join(cache_root,dir_name)
			ori_file_path = os.path.join(cache_root,filename)
			if not os.path.exists(dir_path):
				os.makedirs(dir_path)
			shutil.copy2(ori_file_path,dir_path)
			os.remove(ori_file_path)

def format_local_db(cache_root):
	db_file = os.path.join(cache_root,'localdb')
	db_conn = sqlite3.connect(db_file)
	select_all_sql = "select * from cache2"
	if db_conn:
		cursor = db_conn.cursor()
		cursor.execute(select_all_sql)
		rows = cursor.fetchall()
		cursor.close()
		cursor = db_conn.cursor()
		for row in rows:
			das = json.loads(str(row[1]))
			resid = str(row[0])
			ndas = {}
			ndas['datas']=[]
			ndas['sheets']=[]
			if das and len(das['datas'])>0 and len(das['sheets'])>0 and not "/" in das['datas'][0] and not "/" in das['sheets'][0]:
				for data in das['datas']:
					name,ext = os.path.splitext(data)
					rename = name[0:2]+"/"+data
					ndas['datas'].append(rename)
				for sheet in das['sheets']:
					name,ext = os.path.splitext(sheet)
					rename = name[0:2]+"/"+sheet
					ndas['sheets'].append(rename)
				update_cache_sql = """update cache2 set cache = '%s' where res_id = '%s'"""%(json.dumps(ndas),resid)
				print(update_cache_sql)
				cursor.execute(update_cache_sql)
		db_conn.commit()
		cursor.close()
		db_conn.close()

if __name__ == '__main__':
	cache_root = "/data/work/temp/tpchache"
	format_tp_dir(cache_root)
	format_local_db(cache_root)