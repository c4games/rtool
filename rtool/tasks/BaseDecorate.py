#coding=utf-8
import os
import os.path
from rtool.tasks.Base import Base
from rtool.tasks.BaseParseConfigs import global_cfg_dict
from rtool.tasks.BaseLocalChange import DELETED_DIR_LIST

deleted_file_pattern = []


class BaseDecorate(Base):
	"""
	根据项目组自定规则将输入路径映射到输出路径
	"""
	def __init__(self, options):
		super(BaseDecorate, self).__init__(options)
		self.arg = options

	def inToOut(self,input_path):
		output_path = ""
		return output_path

	def outToIn(self,output_path):
		input_path = ""
		return input_path

	def parseDeletedFilePattern(self):
		input_base = os.path.normpath(self.options['input'])
		work_base = os.path.normpath(self.options['cachedir'])
		work_pack_base = os.path.join(work_base,'pack',self.options['game'],self.options['target'])
		work_compress_base = os.path.join(work_base,'compress',self.options['game'],self.options['target'])
		target = self.options['target']
		
		for dir_path in DELETED_DIR_LIST:
			rel_path = os.path.relpath(dir_path,input_base)


		pass



	# 根据项目规则通过传入已删除的输入文件目录列表，生成对应的输出删除项列表
	def deletedListInToOut(self,deleted_list):
		deleted_output_list = []

		return deleted_output_list

	def outputPathDeleted(self,input_deleted_dir_list,output_path):
		is_deleted = False

		return is_deleted

