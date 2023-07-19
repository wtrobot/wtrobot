import os
import logging
from collections import OrderedDict
from wtrobot.utils.util import Utils
from wtrobot.wt_lib.actions import Actions
from .testscript_parser import TestScriptParser

class Parser:

    def __init__(self, global_conf):
        
        # print("in command parser")
        self.global_conf = global_conf
        # read the given testscript from testscript path
        testdir = Utils.get_abs_filepath(self.global_conf["test_dir_path"])
        self.testfile = os.path.join(testdir,self.global_conf["entry_test_script"])
        self.testscript = Utils.yaml_loader(self.testfile)
        # self.obj_action = Actions(self.global_conf)
        
        # initate parser
        ts_obj = TestScriptParser()
        ts_obj.tsparser(testfile=self.testfile, testscript=self.testscript, global_conf=self.global_conf)
        
        # self.testscript_parser()