#coding=utf-8

import os
import sys

from rtool import utils
from rtool.jobs.config.CommonExportConfigJob import CommonExportConfigJob

class ExportConfigJob(CommonExportConfigJob):
    def __init__(self, options):
        CommonExportConfigJob.__init__(self, options)

    def export_xls_to_json(self):
        from rtool.projects.demo.config.ReadXlsJob import ReadXlsJob
        job = ReadXlsJob(self._options)
        job.run()
