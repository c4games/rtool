#coding=utf-8

import os
import shutil
import click
from .. import utils
# from md5sum_of_path import md5_for_file
# from md5sum_of_path import md5_for_str
# from md5sum_of_path import md5_for_str

from .md5sum_of_command import md5sum_of_command

logger = utils.getLogger('Cache')

saved_cache_dir = None
enable_cache = True

def set_cache_dir(cache_dir):
    global saved_cache_dir
    saved_cache_dir = cache_dir

def set_enable(enable):
    global enable_cache
    enable_cache = enable

def save_cache_for_action_withMD5(action, md5_value, result_file_or_list, opts = None):
    if saved_cache_dir == None:
        return False
    cache_dir = os.path.join(saved_cache_dir,action)
    md5_path = os.path.join(cache_dir, md5_value)

    if os.path.exists(md5_path):
        shutil.rmtree(md5_path)

    os.makedirs(md5_path)
    if type(result_file_or_list) != list:
        result_file_or_list = [result_file_or_list]
    for i in range(len(result_file_or_list)):
        shutil.copy(result_file_or_list[i], md5_path)
    logger.debug('[%s]save cache : %s', cache_dir, md5_path)

def save_cache_for_action(action, input_filepath_or_list, result_file_or_list, opts = None):
    if saved_cache_dir == None:
        return False
    cache_dir = os.path.join(saved_cache_dir,action)
    md5 = get_md5(input_filepath_or_list,opts)
    md5_path = os.path.join(cache_dir, md5)

    if os.path.exists(md5_path):
        shutil.rmtree(md5_path)

    os.makedirs(md5_path)
    if type(result_file_or_list) != list:
        result_file_or_list = [result_file_or_list]
    for i in range(len(result_file_or_list)):
        shutil.copy(result_file_or_list[i], md5_path)
    logger.debug('[%s]save cache : %s', cache_dir, md5_path)


def get_cache_for_action(action, input_filepath_or_list, result_dir, opts = None):
    if saved_cache_dir == None or not enable_cache:
        return False
    cache_dir = os.path.join(saved_cache_dir,action)
    md5 = get_md5(input_filepath_or_list, opts)
    md5_path = os.path.join(cache_dir, md5)
    if os.path.exists(md5_path):
        logger.debug('use_cache_for_action : %s, %s', input_filepath_or_list, result_dir)
        # logger.debug('use cache : ' + input_file_or_path)
        for dirpath, dirnames, filenames in os.walk(md5_path):
            for filename in filenames:
                fname = os.path.join(md5_path, filename)
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
                shutil.copy(fname, result_dir)
        return True
    return False

def get_md5(input_filepath_or_list, opts):

    flag_arguments = []
    key_value_arguments = {}

    if type(opts) == str:
        opts = [opts]

    if type(opts) == list:
        flag_arguments = opts

    if type(opts) == dict:
        key_value_arguments = opts

    return md5sum_of_command(input_filepath_or_list, flag_arguments, key_value_arguments)


@click.command()
@click.option('-s', '--source-asset-path', required = True, help='源目录')
@click.option('-o', '--output-asset-path', required = True, help='导出目录')
@click.option('-C', '--cache-dir', required=True, help='TP缓存目录')
def test(**options):
    input_file = options['source_asset_path']
    output_file_path = options['output_asset_path']

    if not get_cache_for_action('test', input_file, output_file_path, '', options['cache_dir']):
        file_name = os.path.basename(input_file)
        output_name = os.path.join(output_file_path,file_name)
        utils.writeJsonFileByDic(output_name,[1,2,3],True)
        save_cache_for_action('test', input_file, output_name, '', options['cache_dir'])
