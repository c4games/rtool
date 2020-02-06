#coding=utf-8
import os
import os.path
from BaseParseConfigs import task_settings

"""
资源处理中的一个问题是各项目会有一系列“潜规则”，在这些项目组内成员都不一定全清楚的规则下，将资源处理的产出文件更名到产出路径下。例如产出目录结构规则，产出文件的文件名命名规则等。
对于资源处理过程来说，这种没有明确表述的规则是巨大的隐患。
另一方面，如果系统能够通用，那么系统内的规则应该是统一的。并且按照规则进行的路径更名操作应是等价变换操作，输入路径和输出路径能够互相映射。项目组规则往往做不到这一点。
因此采取的策略是资源处理的所有结果都按照输入文件路径的目录结构生成至工作目录中，项目组需要理解并严格遵守这个规则，然后按项目组规则将需要的文件的路径更名到产出目录下。

"""
class BasePathRule(Base):
	"""docstring for BasePathRule"""
	def __init__(self, options):
		super(BasePathRule, self).__init__(options)
		self.options = options

	def tempToOutput(self,temp_path):
		output_path = ""
		"""
		由项目组覆盖并实现从temp中的路径映射到output中路径的规则
		"""
		return output_path
		pass
		