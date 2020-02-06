#coding:utf-8
import os
import os.path

class ExtraCfg(object):
	"""base class for generating extra configs"""
	def __init__(self, arg):
		super(ExtraCfg, self).__init__()
		self.cfg =None
		self.cfg_name = arg
	"""继承并实现该方法生成所需的额外配置信息，额外配置信息存储在每条配置信息的extraCfg项里"""
	def genCfg(self,option):
		if not self.cfg ==None and not self.cfg_name=="":
			option['extraCfg'][self.cfg_name] = self.cfg
			return True
		return False
		pass
