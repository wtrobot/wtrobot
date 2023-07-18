import os
import logging
from collections import OrderedDict
from wtrobot.utils.util import Utils
from wtrobot.wt_lib.actions import Actions

class TestCaseParser:
    
    def __init__(self) -> None:        
        pass

    def tcparser(self, testcase_list, testcase_no, testscript, global_conf):
        """
        This function will execute all steps from single testcase
        """

        # init action class
        self.action_obj = Actions(global_conf)
        
        step_list = list()
        for step in testcase_list:
            step_list.append(list(step.keys())[0])

        # if scenario tag not specifed then add empty tag to avoid exception
        if "scenario" not in step_list:
            step_list.insert(0, "scenario")
            tmpdict = OrderedDict([("scenario", None)])
            testcase_list.insert(0, tmpdict)
 
        for step in step_list:
            index = step_list.index(step)
            if step == "scenario":
                logging.info(
                    "Executing testcase: {0} - {1}".format(
                        testcase_no, testcase_list[0]["scenario"]
                    )
                )

            elif isinstance(testcase_list[index], dict):

                # if indentation for step elements are improper
                if not testcase_list[index][step]:
                    logging.error(
                        "Empty step or improper indentation for steps in yaml testscript"
                    )

                # if "targets" mentioned is str then convert to list
                if "targets" in testcase_list[index][step].keys() and isinstance(
                    testcase_list[index][step]["targets"], str
                ):
                    logging.error(
                        "Targets specified must be list in testcase:{0} step: {1} in yaml testscript".format(
                            testcase_no, step
                        )
                    )
                    tmp = testcase_list[index][step]["targets"]
                    testcase_list[index][step]["targets"] = list([tmp])

                # if "targets" not specified in yaml script then create a list and copy target value init
                if (
                    "targets" not in testcase_list[index][step].keys()
                    and "target" in testcase_list[index][step].keys()
                ):
                    testcase_list[index][step]["targets"] = list(
                        [testcase_list[index][step]["target"]]
                    )

                # if "targets" specified and no "target" then copy first element from targets
                elif (
                    "targets" in testcase_list[index][step].keys()
                    and "target" not in testcase_list[index][step].keys()
                ):
                    testcase_list[index][step]["target"] = testcase_list[index][step][
                        "targets"
                    ][0]

                # if action is import
                if testcase_list[index][step]["action"] == "import":
                    tmp_testcase_no = testcase_list[index][step]["target"]
                    index2 = self.global_testcase_no_list.index(tmp_testcase_no)
                    testscript["test"][index2][
                        tmp_testcase_no
                    ] = self.tcparser(
                        testcase_list=testscript["test"][index2][tmp_testcase_no],
                        testcase_no=tmp_testcase_no,
                    )

                # check if specified action exist
                elif testcase_list[index][step]["action"] in dir(self.action_obj):
                    testcase_list[index][step]["step_no"] = step
                    testcase_list[index][step]["testcase_no"] = testcase_no

                    # call respective function
                    method_name = testcase_list[index][step]["action"]
                    testcase_list[index][step] = getattr(self.action_obj, method_name)(
                        testcase_list[index][step]
                    )

                    # cleanup
                    testcase_list[index][step].pop("step_no")
                    testcase_list[index][step].pop("testcase_no")
                    if "element_obj" in testcase_list[index][step].keys():
                        testcase_list[index][step].pop("element_obj")

                    # Exit loop if error bit set for testcase
                    if (
                        "error" in testcase_list[index][step].keys()
                        and testcase_list[index][step]["error"] == True
                    ):
                        testcase_list[index][step].pop("error")
                        logging.warning(
                            "Exiting testcase:{0} due to failure in step:{1}".format(
                                testcase_no, step
                            )
                        )
                        self.action_obj.closebrowser(testcase_list[index][step])
                        break

                else:
                    logging.error(
                        "INVALID COMMAND '{0}' in {1} at {2}".format(
                            testcase_list[step_list.index(step)][step]["action"],
                            testcase_no,
                            step,
                        )
                    )
                    self.action_obj.closebrowser(testcase_list[index][step])
                    break

        return (testcase_list, testscript)