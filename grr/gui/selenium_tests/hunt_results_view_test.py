#!/usr/bin/env python
# -*- mode: python; encoding: utf-8 -*-
"""Test the hunt results interface."""


import mock
import unittest
from grr.gui import api_call_router_with_approval_checks
from grr.gui import gui_test_lib
from grr.gui.api_plugins import hunt as api_hunt

from grr.lib import flags


class TestHuntResultsView(gui_test_lib.GRRSeleniumHuntTest):

  def testHuntResultsView(self):
    self.CreateGenericHuntWithCollection()

    self.Open("/")
    self.WaitUntil(self.IsElementPresent, "client_query")
    self.Click("css=a[grrtarget=hunts]")

    self.WaitUntil(self.IsTextPresent, "GenericHunt")
    self.Click("css=td:contains('GenericHunt')")

    # Click the Results tab.
    self.Click("css=li[heading=Results]")

    self.WaitUntil(self.IsTextPresent, "aff4:/sample/1")
    self.WaitUntil(self.IsTextPresent,
                   "aff4:/C.0000000000000001/fs/os/c/bin/bash")
    self.WaitUntil(self.IsTextPresent, "aff4:/sample/3")

    self.RequestAndGrantClientApproval("C.0000000000000001")

    self.Click("link=aff4:/C.0000000000000001/fs/os/c/bin/bash")
    self.WaitUntil(self.IsElementPresent,
                   "css=li.active a:contains('Browse Virtual Filesystem')")

  def testDownloadAsPanelNotShownForEmptyHuntResults(self):
    hunt_urn = self.CreateGenericHuntWithCollection([])

    self.Open("/#/hunts/%s/results" % hunt_urn.Basename())

    self.WaitUntil(self.IsTextPresent, "Value")
    self.WaitUntilNot(self.IsElementPresent, "css=grr-download-collection-as")

  @mock.patch.object(api_call_router_with_approval_checks.
                     ApiCallRouterWithApprovalChecksWithRobotAccess,
                     "GetExportedHuntResults")
  def testHuntResultsCanBeDownloadedAsCsv(self, mock_method):
    self.checkHuntResultsCanBeDownloadedAsType(mock_method, "csv-zip",
                                               "CSV (Zipped)")

  @mock.patch.object(api_call_router_with_approval_checks.
                     ApiCallRouterWithApprovalChecksWithRobotAccess,
                     "GetExportedHuntResults")
  def testHuntResultsCanBeDownloadedAsYaml(self, mock_method):
    self.checkHuntResultsCanBeDownloadedAsType(
        mock_method, "flattened-yaml-zip", "Flattened YAML (Zipped)")

  @mock.patch.object(api_call_router_with_approval_checks.
                     ApiCallRouterWithApprovalChecksWithRobotAccess,
                     "GetExportedHuntResults")
  def testHuntResultsCanBeDownloadedAsSqlite(self, mock_method):
    self.checkHuntResultsCanBeDownloadedAsType(mock_method, "sqlite-zip",
                                               "SQLite Scripts (Zipped)")

  def checkHuntResultsCanBeDownloadedAsType(self, mock_method, plugin,
                                            plugin_display_name):
    hunt_urn = self.CreateGenericHuntWithCollection()

    self.Open("/#/hunts/%s/results" % hunt_urn.Basename())
    self.Select("id=plugin-select", plugin_display_name)
    self.Click("css=grr-download-collection-as button[name='download-as']")

    def MockMethodIsCalled():
      try:
        mock_method.assert_called_once_with(
            api_hunt.ApiGetExportedHuntResultsArgs(
                hunt_id=hunt_urn.Basename(), plugin_name=plugin),
            token=mock.ANY)

        return True
      except AssertionError:
        return False

    self.WaitUntil(MockMethodIsCalled)


def main(argv):
  # Run the full test suite
  unittest.main(argv)


if __name__ == "__main__":
  flags.StartMain(main)
