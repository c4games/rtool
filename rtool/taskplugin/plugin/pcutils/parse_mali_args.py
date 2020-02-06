#coding=utf-8
import argparse
def parse_mali_args(s):
	parser = argparse.ArgumentParser(description='mali')
	parser.add_argument('io_image_paths',nargs='+')
	parser.add_argument('-aa', action='store_true')
	parser.add_argument('-as', action='store_true')
	parser.add_argument('-ar', action='store_true')
	parser.add_argument('-ktx', action='store_true')
	parser.add_argument('-v', action='store_true')
	parser.add_argument('-progress', action='store_true')
	parser.add_argument('-version', action='store_true')
	parser.add_argument('-mipmaps', action='store_true')
	parser.add_argument('-s')
	parser.add_argument('-e')
	parser.add_argument('-c')
	parser.add_argument('-f')
	parser.add_argument('-ext')
	args = parser.parse_args(s)

	image_path = None
	key_value_arguments = {}
	flag_arguments = []

	d = vars(args)
	for k in d:
		if d[k] != None and d[k]!=False:
			if k == 'io_image_paths':
				io_image_paths = d[k]
			elif d[k] == True:
				flag_arguments.append(k)
			else:
				key_value_arguments[k] = d[k]
	
	return (io_image_paths,flag_arguments,key_value_arguments)
	pass