#coding=utf8
import sys
import os
import subprocess
import tempfile
import rtool.utils as utils
from .pcutils.parse_texturepacker_args import parse_texturepacker_args
from .pcutils.parse_texturepacker_args import create_texturepacker_args
from .pcutils.md5sum_of_path import md5sum_of_path
from .pcutils.md5sum_of_path import md5_for_str
from .pcutils.expand_path_template_to_real_pathes import expand_path_template_to_real_pathes
from .pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json

class TPTask:
    command = None
    filters = None
    input_files = None
    data_file = None
    sheet_file = None

    _flag_arguments = None
    _key_value_arguments = None
    _task_id = None

    def __init__(self):
        self.logger = utils.getLogger(__name__)

    def _update_arguments(self):
        if self._flag_arguments == None or self._key_value_arguments == None:
            image_path,flag_arguments,key_value_arguments = parse_texturepacker_args(self.command[1:])
            self._flag_arguments = flag_arguments
            self._key_value_arguments = key_value_arguments

    def flag_arguments(self):
        self._update_arguments()
        return self._flag_arguments

    def key_value_arguments(self):
        self._update_arguments()
        return self._key_value_arguments

    def __str__(self):
        return ' '.join(self.command)

    def get_task_id(self):
        if self._task_id != None:
            return self._task_id

        img_md5 = md5sum_of_path(self.input_files)
        if img_md5 == None:
            # 空目录
            return None

        flag_arguments = self.flag_arguments()
        key_value_arguments = self.key_value_arguments()

        args_str=""
        #['quiet', 'multipack']
        if len(flag_arguments) > 0:
            flag_arguments.sort()
            args_str = "=".join(flag_arguments)

        #{'opt': 'PVRTC4','format': 'cocos2d'}
        key_list = list(key_value_arguments.keys())
        if len(key_list) > 0:
            key_list.sort()
            for k in key_list:
                if k != "data" and k != "sheet":
                    v = key_value_arguments.get(k,"")
                    args_str += (k + "=" + v)
                else:
                    # 输入参数中的 sheet name 会影响到 data 输出的plist文件里面的 textureFileName
                    # 所以考虑唯一性时也要算进去
                    v = key_value_arguments.get(k,"")
                    args_str += (k + "=" + os.path.basename(v))

        args_md5 = md5_for_str(args_str)

        res_md5 = md5_for_str(args_md5 + img_md5)
        self._task_id = res_md5
        return self._task_id

    def run(self):
        # 此处可能会抛异常
        # output = subprocess.check_output(self.command)
        #lixu 使用check_output时，所执行进程返回结果时并不一定已经终止，所以可能造成一些文件没有完成写入时run函数就返回了，当后续操作需要删除该文件时就会出现问题
        output =""
        f = tempfile.TemporaryFile()
        process = subprocess.Popen(self.command,stdout=f, stderr=f, stdin=subprocess.PIPE)
        process.wait()        
        f.seek(0)
        output = f.read()
        if not process.returncode==0:
            self.logger.error("［错误］合图出现问题 "+str(output))
            sys.exit(1)

        paths = expand_path_template_to_real_pathes(self.data_file)
        for p in paths:
            if os.path.exists(p):
                remove_smartupdate_from_plist_or_json(p)
        return output

    def get_ouput_sheet_files(self):
        return expand_path_template_to_real_pathes(self.sheet_file)

    def get_ouput_data_files(self):
        return expand_path_template_to_real_pathes(self.data_file)

    @staticmethod
    def task_from_command(command):
        task = TPTask()
        task.command = command
        task.filters = None

        image_path,flag_arguments,key_value_arguments = parse_texturepacker_args(command[1:])

        task.input_files = image_path
        task.data_file = key_value_arguments['data']
        task.sheet_file = key_value_arguments['sheet']

        return task

    @staticmethod
    def testest():
        pass

