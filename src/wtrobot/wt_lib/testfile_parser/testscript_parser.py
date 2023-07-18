import os
import logging
from collections import OrderedDict
from wtrobot.utils.util import Utils
from wtrobot.wt_lib.actions import Actions
from .testcase_parser import TestCaseParser

class TestScriptParser:
    
    def __init__(self) -> None:
        pass
    
    def tsparser(self, testfile, testscript, global_conf):
        """
        This function will iterate through entire testscript dict from test file 
        """
        logging.info("command parser init")

        sequence_testcase_no_list = list()
        global_testcase_no_list = list()

        # print(testscript)
        for testcase in testscript["test"]:
            global_testcase_no_list.append(list(testcase.keys())[0])

        # if sequence key is mentioned then follow the sequence else the dict sequence
        if "sequence" in testscript.keys():
            sequence_testcase_no_list = testscript["sequence"]
        else:
            sequence_testcase_no_list = global_testcase_no_list

        for testcase in sequence_testcase_no_list:
            index = global_testcase_no_list.index(testcase)
            # testcase parser init
            tc_obj = TestCaseParser()
            testscript["test"][index][testcase],testscript = tc_obj.tcparser(
                testcase_list = testscript["test"][index][testcase],
                testcase_no = testcase,
                testscript = testscript,
                global_conf = global_conf,
            )

        # update script file
        Utils.yaml_dump(
            filepath=testfile, data=testscript
        )