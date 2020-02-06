#coding=utf-8

import yaml
import os
import logging
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import ansistrm as am

def getLogger(name):
    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger

    # console = logging.StreamHandler()
    console = am.ColorizingStreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    return logger

main_config = None

logger = getLogger(__name__)

def dumpOptions(obj, logger):
    logger.info('Input Options:')
    for k in obj:
        v = obj[k]
        logger.info(k + " = " + str(v))

def is_true(v):
    return v=='1' or v=='yes' or v=='true' or v == True

def getMainConfig(key = None):
    global main_config
    if main_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir, 'config.yaml')
        print config_path
        if not os.path.exists(config_path):
            logger.error("config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
            exit()
        stream = file(config_path, 'r')
        main_config = yaml.load(stream)
    if key != None:
        if main_config.has_key(key):
            return main_config[key]
        else:
            return None
    return main_config

project_config = None
personal_config = None

def getProjectConfig(key):
    global project_config
    global personal_config

    if personal_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir, 'config.personal.yaml')
        if os.path.exists(config_path):
            stream = file(config_path, 'r')
            personal_config = yaml.load(stream)
        if personal_config == None:
            personal_config = {}
    if project_config == None:
        config = getMainConfig()
        project_name = config['project_name']
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir, 'config.' + project_name + '.yaml')
        print config_path
        if not os.path.exists(config_path):
            logger.error("config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
            exit()
        stream = file(config_path, 'r')
        project_config = yaml.load(stream)
        if project_config == None:
            project_config = {}
    if key != None:
        if personal_config.has_key(key):
            return personal_config[key]
        elif project_config.has_key(key):
            return project_config[key]
        else:
            return None
    return project_config

def remove_dir(dir_path):
    if not os.path.exists(dir_path):
        return
    dir_path = dir_path + os.sep
    list = os.listdir(dir_path)
    for li in list:
        filepath = os.path.join(dir_path,li)
        if os.path.isdir(filepath):
            remove_dir(filepath)
        elif os.path.isfile(filepath):
            os.remove(filepath)

        if os.path.exists(filepath):
            os.rmdir(filepath)

def getMtlCurPath():
    path = os.getcwd()
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def relativePath(base_path,path):
    return path.replace(base_path,'')
    pass

def md5_for_file(orig_data):
    md5 = hashlib.md5()
    block_size=2**20
    f = open(orig_data, 'rb')
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    return md5.hexdigest()


def md5_for_str(s):
    md5 = hashlib.md5()
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()


def md5sum_of_path(paths, extensions = None):
    """计算指定路径下所有文件的  文件名和内容的md5sum

    只有所有文件的内容和文件名都一致时, 得出的md5才会相同
    """
    if type(paths) == str:
        paths = [paths]
    md5_str = ""
    img_list = []
    for fORd in paths:
        if not os.path.exists(fORd):
            raise Exception(fORd + " not exist") 

        if os.path.isfile(fORd):
            img_list.append(fORd)
        else:
            for rt, dirs, files in os.walk(fORd):
                for f in files:
                    suffix = os.path.splitext(f)[1]
                    if extensions == None or suffix in extensions:
                        img_list.append(os.path.join(rt,f))

    if len(img_list) == 0:
        return None

    img_list.sort()
    for img in img_list:
        md5_str += os.path.basename(img)
        md5_str += md5_for_file(img)
    return md5_for_str(md5_str)

def md5sum_of_IOpath(input_file_list,options,paths, extensions = None):
    """
        加入输入文件列表的文件名一起计算，这样输入或输出资源发生变动时都能反应在md5值上
    """
    if type(paths) == str:
        paths = [paths]
    md5_str = ""
    img_list = []
    for fORd in paths:
        if not os.path.exists(fORd):
            if os.path.isfile(fORd):
                img_list.append(fORd)
            else:
                for rt, dirs, files in os.walk(fORd):
                    for f in files:
                        suffix = os.path.splitext(f)[1]
                        if extensions == None or suffix in extensions:
                            img_list.append(os.path.join(rt,f))

    if len(img_list) == 0:
        md5_str = "nooutput"

    img_list.sort()
    for img in img_list:
        md5_str += os.path.basename(img)
        md5_str += md5_for_file(img)
        if input_file_list:
            for img_path in input_file_list:
                md5_str += md5_for_file(img_path)
        md5_str += str(options)
    return md5_for_str(md5_str)

""" 
lixu 20180130
windows默认的编码是cp1252，windows的控制台程序需要此编码路径，python中的数据结构在存储字符串时是以assii形式存储的
因此json，yaml，plist，logger等库在处理汉字路径时会遇到不同的问题，例如路径截断或编码错误
目前的解决方案是在需要内部结构－》序列化结构的时候用encodePath处理路径，在使用控制台工具时使用decodePath
"""
def encodePath(text):
    if sys.platform =="win32":
        # return text.decode('cp936').encode('utf-8')
        return text.decode('utf-8')
    else:
        return text

def decodePath(text):
    if sys.platform == "win32":
        # return text.decode('utf-8').encode('cp936')
        return text.decode('utf-8')
    else:
        return text

if __name__ == '__main__':
    #getProjectConfig('')
    print md5sum_of_path('/Users/playcrab/Desktop/workforme/aaaa')
    print md5sum_of_path('/Users/playcrab/Desktop/workforme/bbbb')