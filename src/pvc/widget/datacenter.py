# Copyright (c) 2015 Marin Atanasov Nikolov <dnaeon@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Datacenter Widgets

"""

import pyVmomi

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.cluster
import pvc.widget.debug
import pvc.widget.event
import pvc.widget.hostsystem
import pvc.widget.menu
import pvc.widget.performance
import pvc.widget.virtualmachine

__all__ = [
    'DatacenterWidget', 'DatacenterActionWidget',
    'DatacenterClusterWidget', 'DatacenterHostSystemWidget',
    'DatacenterDatastoreWidget', 'DatacenterNetworkWidget',
    'DatacenterVirtualMachineWidget',
]


class DatacenterWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Datacenter Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Summary',
                description='General information',
                on_select=self.summary
            ),
            pvc.widget.menu.MenuItem(
                tag='Actions',
                description='Available Action',
                on_select=DatacenterActionWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Configuration',
                description='Datacenter configuration'
            ),
            pvc.widget.menu.MenuItem(
                tag='Clusters',
                description='Manage clusters in datacenter',
                on_select=DatacenterClusterWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Hosts',
                description='Manage hosts in datacenter',
                on_select=DatacenterHostSystemWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Virtual Machines',
                description='Manage Virtual Machines in datacenter',
                on_select=DatacenterVirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastore',
                description='Manage datastores in datacenter',
                on_select=DatacenterDatastoreWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Networking',
                description='Manage networking in datacenter',
                on_select=DatacenterNetworkWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Performance',
                description='Performance Metrics',
                on_select=pvc.widget.performance.PerformanceProviderWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Events',
                description='View Events',
                on_select=pvc.widget.event.EventWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Alarms',
                description='View triggered alarms',
                on_select=pvc.widget.common.alarm_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Debug',
                description='Start a Python REPL console',
                on_select=pvc.widget.debug.DebugWidget,
                on_select_args=(locals(), globals())
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select item from menu'
        )

        menu.display()

    def summary(self):
        """
        Datacenter general information

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Overall Status',
                item=self.obj.overallStatus
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Datacenter general information'
        )

        form.display()


class DatacenterActionWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Datacenter Actions Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Rename',
                description='Rename datacenter',
                on_select=pvc.widget.common.rename,
                on_select_args=(self.obj, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Remove',
                description='Remove datacenter',
                on_select=pvc.widget.common.remove,
                on_select_args=(self.obj, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()


class DatacenterClusterWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Datacenter Cluster Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Create',
                description='Create new cluster in datacenter',
                on_select=self.create_cluster
            ),
            pvc.widget.menu.MenuItem(
                tag='Remove',
                description='Remove cluster from datacenter'
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View clusters in datacenter',
                on_select=pvc.widget.common.cluster_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()

    def create_cluster(self):
        """
        Create a new cluster in the datacenter

        """
        code, name = self.dialog.inputbox(
            title=self.title,
            text='Provide name for the cluster to be created'
        )

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not name:
            self.dialog.msgbox(
                title=self.title,
                text='Error, invalid input provided'
            )
            return

        self.dialog.infobox(
            title=self.title,
            text='Creating cluster {} ...'.format(name)
        )

        try:
            self.obj.hostFolder.CreateClusterEx(
                name=name,
                spec=pyVmomi.vim.cluster.ConfigSpecEx()
            )
        except pyVmomi.vim.MethodFault as e:
            self.dialog.msgbox(
                title=self.title,
                text=e.msg
            )


class DatacenterHostSystemWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing hosts in a datacenter

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View hosts in datacenter',
                on_select=self.host_menu
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select item from menu'
        )

        menu.display()

    def host_menu(self):
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        view = self.agent.get_container_view(
            obj_type=[pyVmomi.vim.HostSystem],
            container=self.obj
        )
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.HostSystem,
            path_set=['name', 'runtime.connectionState'],
            include_mors=True
        )
        view.DestroyView()

        if not properties:
            self.dialog.msgbox(
                title=self.title,
                text='No hosts found in datacenter'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=host['name'],
                description=host['runtime.connectionState'],
                on_select=pvc.widget.hostsystem.HostSystemWidget,
                on_select_args=(self.agent, self.dialog, host['obj'])
            ) for host in properties
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select a host from the menu'
        )

        menu.display()


class DatacenterDatastoreWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing datastores in a datacenter

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View datastores in datacenter',
                on_select=pvc.widget.common.datastore_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select item from menu'
        )

        menu.display()


class DatacenterNetworkWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing networking in a datacenter

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View networks in datacenter',
                on_select=pvc.widget.common.network_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select item from menu'
        )

        menu.display()


class DatacenterVirtualMachineWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing virtual machines in a datacenter

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Create',
                description='Create new Virtual Machine',
                on_select=pvc.widget.virtualmachine.CreateVirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='Virtual Machines in datacenter',
                on_select=self.virtual_machine_menu
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()

    def virtual_machine_menu(self):
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        view = self.agent.get_container_view(
            obj_type=[pyVmomi.vim.VirtualMachine],
            container=self.obj
        )
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.VirtualMachine,
            path_set=['name', 'runtime.powerState'],
            include_mors=True
        )
        view.DestroyView()

        if not properties:
            self.dialog.msgbox(
                title=self.title,
                text='No virtual machines found in datacenter'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm['name'],
                description=vm['runtime.powerState'],
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm['obj'])
            ) for vm in properties
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select a virtual machine from the menu'
        )

        menu.display()
