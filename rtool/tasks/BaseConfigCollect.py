#coding=utf-8
import os
import os.path
from rtool.tasks.Base import Base
import rtool.utils as utils

class BaseConfigCollect(Base):
	"""docstring for BaseConfigCollect"""
	def __init__(self, options):
		super(BaseConfigCollect, self).__init__(options)
	
	def genResYamlHash(self,yaml_diff_dict,res_diff_dict):
		added_yaml_list = yaml_diff_dict.get('Added',[])
		changed_yaml_list = yaml_diff_dict.get('Changed',[])
		deleted_yaml_list = yaml_diff_dict.get('Deleted',[])
		added_and_changed_yaml_list = added_yaml_list+changed_yaml_list	
		res_yaml_hash={}
		# 1.直接由变更文件列表中的yaml文件生成，即yaml文件为新增或变更。这种情况下yaml所在目录及起子目录都会受到影响
		# 3.资源文件变化，同时资源文件所在的目录或其上层目录有变更的yaml文件，此时变更yaml解析出的配置信息会覆盖同一目录的原配置信息
		for yaml_path in added_and_changed_yaml_list:
			yaml_dir,yaml_file_name = os.path.split(yaml_path)
			for par,dirnames,fnames in os.walk(yaml_dir):
				for dirname in dirnames:
					dir_path = os.path.join(par,dirname)
					res_yaml_hash[dir_path] = yaml_path
		# 4.yaml删除，yaml所在目录和子目录中配置项都要由yaml上层目录中的配置文件重新生成
		for yaml_path in deleted_yaml_list:
			yaml_dir,yaml_file_name = os.path.split(yaml_path)
			if os.path.exists(yaml_dir):
				for par,dirnames,fnames in os.walk(yaml_dir):
					for dirname in dirnames:
						dir_path = os.path.join(par,dirname)
						res_yaml_hash[dir_path]="renew"
		# 2.资源文件变化，但是资源文件所在的目录的和其上层目录并没有包含变更的yaml文件，使用之前存储的配置信息
		res_add_list = res_diff_dict.get('Added',[])
		res_changed_list = res_diff_dict.get('Changed',[])
		res_deleted_list = res_diff_dict.get('Deleted',[])
		res_add_and_changed_list = res_add_list+res_changed_list
		for res_path in res_add_and_changed_list:
			need_to_load_config = True
			res_dir_path = os.path.split(res_path)[0]
			for dir_path in res_yaml_hash.keys():
				if dir_path==res_dir_path or utils.is_parent_path(dir_path,res_dir_path):
					need_to_load_config = False
			if need_to_load_config:
				res_yaml_hash[res_dir_path]="stored"
		# 5.资源文件删除，但是目录没有删除，目录项配置不变
		# 6.资源目录整体删除，与目录及其子目录相关的配置均要标记为删除
		for res_path in res_deleted_list:
			res_dir,res_file_name = os.path.split(res_dir)
			if not os.path.exists(res_dir):
				res_yaml_hash[res_dir]='deleted'
		return res_yaml_hash
		pass
