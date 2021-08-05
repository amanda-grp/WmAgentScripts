import os
import logging
from logging import Logger

from Utilities.WebTools import sendResponse
from Utilities.ConfigurationHandler import ConfigurationHandler

from typing import Optional


class ReqMgrWriter(object):
    """
    _ReqMgrWriter_
    General API for writing data in ReqMgr
    """

    def __init__(self, logger: Optional[Logger] = None, **contact):
        try:
            super().__init__()
            configurationHandler = ConfigurationHandler()
            self.reqmgrUrl = os.getenv("REQMGR_URL", configurationHandler.get("reqmgr_url"))
            self.reqmgrEndpoint = {"agentConfig": "/reqmgr2/data/wmagentconfig/", "request": "/reqmgr2/data/request/"}

            logging.basicConfig(level=logging.INFO)
            self.logger = logger or logging.getLogger(self.__class__.__name__)

        except Exception as error:
            raise Exception(f"Error initializing ReqMgrWriter\n{str(error)}")

    def invalidateWorkflow(self, wf: str, currentStatus: str, cascade: bool = False) -> bool:
        """
        The function to invalidate a workflow
        :param wf: workflow name
        :param currentStatus: current workflow status
        :param cascade: if to cascade the info or not
        :return: True if invalidation succeeded, False o/w
        """
        try:
            if currentStatus in ["aborted", "rejected", "aborted-completed", "aborted-archived", "rejected-archived"]:
                self.logger.info("%s already %s, no action required", wf, currentStatus)
                return True

            param = {"RequestStatus": "aborted", "cascade": str(cascade)}
            if currentStatus in ["assignment-approved", "new", "completed", "closed-out", "announced", "failed"]:
                param = {"RequestStatus": "rejected", "cascade": str(cascade)}
            elif currentStatus == "normal-archived":
                param = {"RequestStatus": "rejected-archived"}

            return self.setWorkflowParam(wf, param)

        except Exception as error:
            self.logger.error("Failed to invalidate %s", wf)
            self.logger.error(str(error))
            return False

    def forceCompleteWorkflow(self, wf: str) -> bool:
        """
        The function to force complete a workflow
        :param wf: workflow name
        :return: True if completion succeeded, False o/w
        """
        return self.setWorkflowParam(wf, {"RequestStatus": "force-complete"})

    def setWorkflowParam(self, wf: str, param: dict) -> bool:
        """
        The function set some params to a given workflow
        :param wf: workflow name
        :param param: workflow param
        :return: True if succeeded, False o/w
        """
        try:
            result = sendResponse(url=self.reqmgrUrl, endpoint=self.reqmgrEndpoint["request"] + wf, param=param)
            return any(item.get(wf) == "OK" for item in result["result"])

        except Exception as error:
            self.logger.error("Failed to set %s for %s", param, wf)
            self.logger.error(str(error))
            return False
