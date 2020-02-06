#coding=utf-8

import os

from rtool import utils
from rtool.jobs.config.CommonValueParser import CommonValueParser


class ValueParser(CommonValueParser):

    def __init__(self, options):
        CommonValueParser.__init__(self, options)

    def get_value_by_type(self, data_str, type_str):
        type_str = self.format_field(type_str)
        if type_str == 'auto':
            type_str = 'string'
        if (type(data_str) is str or type(data_str) is unicode) and  '[' in data_str and '[' in type_str:
            data_str = data_str[data_str.find('[')+1:data_str.rfind(']')]
        return CommonValueParser.get_value_by_type(self, data_str, type_str)

    def format_field(self, field_type):
        if '[]' in field_type:
            field_type = '[' + field_type[0:field_type.find('[')] + ']'
        return field_type
