#coding=utf-8
import os
import os.path
from rtool.tasks.Base import Base
from rtool import utils as mut

"""
根据传入SVN路径，获取文件变更信息
"""

DELETED_DIR_LIST = []

class BaseLocalChange(Base):
	"""docstring for BaseLocalChange"""
	def __init__(self, options):
		super(BaseLocalChange, self).__init__(options)
		self.diff_dict = options.get("diff_dict",{})
		self.svn_path = options.get('svn',"")
		self.revision_from = options.get('last_svn_commit','0')
		self.revision_to = options.get('svn_commit','0')
		self.options = options		
		self.modified_dir_list = []
		self.modified_ncfg_list = []
		self.diff_list = []
		self.deleted_dir_list = DELETED_DIR_LIST
		self.deleted_ncfg_list = []

	def processDiff(self):
		print("processDiff")
		self.diff_list = mut.get_svn_diff_xml_list(self.svn_path,self.revision_from,self.revision_to,self.options)
		self.parseDiffList()
		pass
	
	def getAllLocalYamls(self):
		yaml_list = []
		for par,filenames,dirnames in os.walk(self.input_root):
			for filename in filenames:
				name,ext = os.path.splitext(filename)
				if ext == '.yaml':
					yaml_list.append(os.path.join(par,filename))
		return yaml_list
		pass

	def parseDiffList(self):
		for change_tag,path in self.diff_list:
			"""
			对于标记为D的路径，如果是目录，表示输入文件的目录整个被删除了，需要加入deleted_dir_list,后续会根据该列表判断是否使用历史版本处理结果
			如果是ncfg文件，则加入到deleted_ncfg_list中
			其余情况可以视作目录文件变更，和一般的文件变更做同样处理
			"""
			if change_tag == 'D':				
				if '.ncfg.yaml' in path:
					self.deleted_ncfg_list.append(os.path.normpath(path))
				# 对于已删除的目录不能使用os.path.isdir进行判断，因此判断如无后缀名即为目录
				if os.path.splitext(path)[1] == '':
					self.deleted_dir_list.append(os.path.normpath(path))
					self.modified_dir_list.append(os.path.normpath(path))
				else:
					base_dir = os.path.split(path)[0]
					self.modified_dir_list.append(os.path.normpath(base_dir))
				pass
			
			if os.path.isfile(path):
				modified_dir = os.path.split(path)[0]
				if '.ncfg.yaml' in path:
					self.modified_ncfg_list.append(os.path.normpath(path))
				else:
					self.modified_dir_list.append(os.path.normpath(modified_dir))
			elif os.path.isdir(path):
				self.modified_dir_list.append(os.path.normpath(path))
			pass

		self.modified_dir_list = list(set(self.modified_dir_list))
		self.modified_ncfg_list = list(set(self.modified_ncfg_list))

		self.deleted_dir_list = list(set(self.deleted_dir_list))
		self.deleted_ncfg_list = list(set(self.deleted_ncfg_list))
		pass

	def parseResDirNeedToModify(self):
		res_dir_need_to_modify = {}
		for dir_path in self.add_dir_list:
			res_dir_need_to_modify[dir_path]="A"
		for dir_path in self.modified_dir_list:
			res_dir_need_to_modify[dir_path]="M"
		for dir_path in self.deleted_dir_list:
			res_dir_need_to_modify[dir_path]="D"
		pass	



if __name__ == '__main__':
	# diff_dict = {"Added":["xxx/xxx/xxx.png","yyy/yy/yyy.yaml"],"Changed":["",""],"Deleted":["",""]}
	options={}
	options['path']=''
	options['input']=''
	options['output']=''
	options['cachedir']=''
	options['game']=''
	input_root = mut.getProjectConfig('input_root')
	rtool_root = mut.getProjectConfig('rtool_root')
	output_root = mut.getProjectConfig('output_root')
	cache_dir = mut.getProjectConfig('cache_dir')
	if options['path'] == '':
	    options['path'] = rtool_root
	if options['input'] == '':
	    options['input'] = os.path.join(input_root)
	if options['output'] == '':
	    options['output'] = os.path.join(output_root)
	if options['cachedir'] =='':
	    options['cachedir'] = cache_dir
	if options['game'] == '':
	    options['game'] = mut.getMainConfig('project_name')
	svn_path = "/data/work/Assets"
	options['svn'] = svn_path
	options['svn_commit'] = '33734'
	options['last_svn_commit'] = '33733'
	options['target']='iOS'
	blc = BaseLocalChange(options)	
	# blc.diff_dict = all_file_as_added_dict	
	# print blc.getYamlDiffDict()
	# print blc.getResDiffDict()
	blc.processDiff()
	print("diff list")
	print(blc.diff_list)
	print("modified dir list")
	print(blc.modified_dir_list)
	# print "modified ncfg list"
	# print blc.modified_ncfg_list
	# print "deleted dir"
	# print blc.deleted_dir_list
	# print "deleted ncfg list"
	# print blc.deleted_ncfg_list

	# for par,dirnames,_ in os.walk(svn_path):
	# 	for dirname in dirnames:
	# 		dir_path = os.path.normpath(os.path.join(par,dirname))
	# 		if not dir_path in blc.modified_dir_list:
	# 			print dir_path
