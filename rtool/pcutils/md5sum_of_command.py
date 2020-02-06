#coding=utf8

import hashlib
import os

from .md5sum_of_path import md5sum_of_path
from .md5sum_of_path import md5_for_str


def md5sum_of_command(input_paths, flag_arguments, key_value_arguments):

    img_md5 = md5sum_of_path(input_paths)
    if img_md5 is None:
        # 空目录
        return None

    args_str = ""
    # ['quiet', 'multipack']
    if len(flag_arguments) > 0:
        flag_arguments.sort()
        args_str = "=".join(flag_arguments)

    # {'opt': 'PVRTC4','format': 'cocos2d'}
    key_list = key_value_arguments.keys()
    # if len(key_list) > 0:
    #     key_list.sort()
    #     for k in key_list:
    #         if k != "data" and k != "sheet":
    #             v = key_value_arguments.get(k,"")
    #             args_str += (k + "=" + v)
    #         else:
    #             # 输入参数中的 sheet name 会影响到 data 输出的plist文件里面的 textureFileName
    #             # 所以考虑唯一性时也要算进去
    #             v = key_value_arguments.get(k,"")
    #             args_str += (k + "=" + os.path.basename(v))
    if len(key_list) > 0:
        key_list.sort()
        for k in key_list:
            v = key_value_arguments.get(k,"")
            args_str += (k + "=" + v)

    args_md5 = md5_for_str(args_str)

    res_md5 = md5_for_str(args_md5 + img_md5)

    return res_md5