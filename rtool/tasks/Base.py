#coding=utf-8

class Base(object):
	"""docstring for Base"""
	def __init__(self, options):
		super(Base, self).__init__()
		self.input_root = options.get("input_root","")
		self.output_root = options.get("output_root","")
		self.rtool_root = options.get("rtool_root","")
		self.cache_dir = options.get("cache_dir","")
		self.project_name = options.get("game","")
