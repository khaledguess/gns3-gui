# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import shutil
from gns3.node import Node
from gns3.qt import QtWidgets
from gns3.utils.sudo import sudo

import logging
log = logging.getLogger(__name__)


class HostOnly(Node):

    """
    HostOnly node

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "host_only"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)
        self._always_on = True
        self._host_only_settings = {}
        self.settings().update(self._host_only_settings)

    def interfaces(self):

        return self._interfaces

    def _getGNS3LoopbackTool(self):
        """
        Get the gns3loopback utility path.
        """

        gns3vmnet = shutil.which("gns3vmnet")
        if gns3vmnet is None:
            QtWidgets.QMessageBox.critical(self, "gns3vmnet", "The gns3vmnet utility is not installed")
            return None
        return gns3vmnet

    def _addWindowsLoopback(self, name):
        """
        Add a Windows loopback adapter.
        """

        gns3loopback = self._getGNS3LoopbackTool()
        if gns3loopback is None:
            return
        command = [gns3loopback, "-add", name, "10.42.1.1", "255.0.0.0"]
        sudo(command, parent=self)

    def create(self, name=None, node_id=None, default_name_format="HostOnly{0}"):
        """
        Creates this host_only.

        :param name: optional name for this host_only
        :param node_id: Node identifier on the server
        """

        if sys.platform.startswith("win"):
            self._addWindowsLoopback(name)

        params = {}
        self._create(name, node_id, params, default_name_format)

    def _createCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        """

        if error:
            log.error("Error while creating host_only: {}".format(result["message"]))
            return

    def update(self, new_settings):
        """
        Updates the settings for this host_only.

        :param new_settings: settings dictionary
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value
        if params:
            self._update(params)

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        """

        if error:
            log.error("Error while creating host_only: {}".format(result["message"]))
            return

    def info(self):
        """
        Returns information about this host_only.

        :returns: formatted string
        """

        info = """HostOnly device {name} is always-on
This is a node for external connections
""".format(name=self.name())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

        return info + port_info

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this host_only.

        :returns: symbol path (or resource).
        """

        return ":/symbols/cloud.svg"

    @staticmethod
    def symbolName():

        return "Host-Only"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "Host-Only"
