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
Cluster Widgets

"""

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.checklist
import pvc.widget.debug
import pvc.widget.event
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.menu
import pvc.widget.performance
import pvc.widget.virtualmachine

__all__ = [
    'ClusterWidget', 'ClusterActionWidget',
    'ClusterHostWidget', 'ClusterVirtualMachineWidget',
]


class ClusterWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

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
                tag='Resources',
                description='Resource usage information',
                on_select=self.resources
            ),
            pvc.widget.menu.MenuItem(
                tag='Actions',
                description='Available Actions',
                on_select=ClusterActionWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Hosts',
                description='Manage hosts in cluster',
                on_select=ClusterHostWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Virtual Machines',
                description='Manage Virtual Machines in cluster',
                on_select=ClusterVirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastores',
                description='Manage datastores',
                on_select=pvc.widget.common.datastore_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Networks',
                description='Networking',
                on_select=pvc.widget.common.network_menu,
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
        Cluster general information

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Hosts',
                item=str(self.obj.summary.numHosts)
            ),
            pvc.widget.form.FormElement(
                label='DRS Enabled',
                item=str(self.obj.configuration.drsConfig.enabled)
            ),
            pvc.widget.form.FormElement(
                label='DRS Mode',
                item=self.obj.configuration.drsConfig.defaultVmBehavior
            ),
            pvc.widget.form.FormElement(
                label='vMotion Migrations',
                item=str(self.obj.summary.numVmotions)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Cores',
                item=str(self.obj.summary.numCpuCores)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Threads',
                item=str(self.obj.summary.numCpuThreads)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Resources',
                item='{} MHz'.format(self.obj.summary.totalCpu)
            ),
            pvc.widget.form.FormElement(
                label='Total Memory',
                item=humanize.naturalsize(self.obj.summary.totalMemory, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Overall Status',
                item=self.obj.overallStatus
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Cluster general information'
        )

        form.display()

    def resources(self):
        """
        Resource usage information

        """
        text = (
            'Not implemented yet.\n'
            'See https://github.com/vmware/pyvmomi/issues/229 '
            'for more details.\n'
        )

        self.dialog.msgbox(
            title=self.title,
            text=text
        )


class ClusterActionWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Actions Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

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
                description='Rename cluster',
                on_select=pvc.widget.common.rename,
                on_select_args=(self.obj, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Remove',
                description='Remove cluster',
                on_select=pvc.widget.common.remove,
                on_select_args=(self.obj, self.agent)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()


class ClusterHostWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Host Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Connect',
                description='Connect host to cluster',
                on_select=self.connect_host
            ),
            pvc.widget.menu.MenuItem(
                tag='Disconnect',
                description='Disconnect host(s) from cluster',
                on_select=self.disconnect_host
            ),
            pvc.widget.menu.MenuItem(
                tag='Reconnect',
                description='Reconnect host(s) to cluster',
                on_select=self.reconnect_host
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View hosts in cluster',
                on_select=pvc.widget.common.host_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select action to be performed'
        )

        menu.display()

    def connect_host(self):
        """
        Connect a host to the cluster and add it to the inventory

        """
        text = (
            'Enter hostname or IP address of the '
            'host to be connected to cluster {}\n'
        )

        elements = [
            pvc.widget.form.FormElement(label='Hostname'),
            pvc.widget.form.FormElement(label='SSL Thumbprint'),
            pvc.widget.form.FormElement(label='Username'),
            pvc.widget.form.FormElement(label='Password', attributes=0x1),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            mixed_form=True,
            title=self.title,
            text=text.format(self.obj.name)
        )

        code, fields = form.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not all(fields.values()):
            self.dialog.msgbox(
                title=self.title,
                text='Invalid input provided'
            )
            return

        connect_spec = pyVmomi.vim.HostConnectSpec(
            hostName=fields['Hostname'],
            sslThumbprint=fields['SSL Thumbprint'],
            userName=fields['Username'],
            password=fields['Password']
        )

        task = self.obj.AddHost(
            spec=connect_spec,
            asConnected=True
        )

        gauge = pvc.widget.gauge.TaskGauge(
            dialog=self.dialog,
            task=task,
            title=self.title,
            text='Connecting {} to cluster ...'.format(fields['Hostname'])
        )

        gauge.display()

    def disconnect_host(self):
        """
        Disconnect host(s) from the cluster

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        items = [
            pvc.widget.checklist.CheckListItem(tag=h.name, description=h.runtime.connectionState)
            for h in self.obj.host if h.runtime.connectionState == pyVmomi.vim.HostSystemConnectionState.connected
        ]

        if not items:
            self.dialog.msgbox(
                title=self.title,
                text='There are no hosts connected to cluster'
            )
            return

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select host(s) to be disconnected from the cluster'
        )

        checklist.display()
        selected = checklist.selected()

        if not selected:
            return

        text = (
            'The following host(s) will be disconnected from cluster.'
            '\n\n{}\n\n'
            'Disconnect host(s) from cluster?\n'
        )
        code = self.dialog.yesno(
            title=self.title,
            text=text.format('\n'.join(selected))
        )

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        host_objects = [h for h in self.obj.host if h.name in selected]
        for host_obj in host_objects:
            task = host_obj.Disconnect()
            gauge = pvc.widget.gauge.TaskGauge(
                title=self.title,
                text='Disconnecting {} from cluster ...'.format(host_obj.name),
                dialog=self.dialog,
                task=task
            )
            gauge.display()

    def reconnect_host(self):
        """
        Reconnect disconnected hosts to cluster

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        items = [
            pvc.widget.checklist.CheckListItem(tag=h.name, description=h.runtime.connectionState)
            for h in self.obj.host if h.runtime.connectionState == pyVmomi.vim.HostSystemConnectionState.disconnected
        ]

        if not items:
            self.dialog.msgbox(
                title=self.title,
                text='There are no disconnected hosts in the cluster'
            )
            return

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select host(s) to be reconnected to the cluster'
        )

        checklist.display()
        selected_hosts = checklist.selected()

        if not selected_hosts:
            return

        host_objects = [h for sh in selected_hosts for h in self.obj.host if sh == h.name]
        for host_obj in host_objects:
            task = host_obj.Reconnect()
            gauge = pvc.widget.gauge.TaskGauge(
                title=self.title,
                text='Reconnecting {} to cluster ...'.format(host_obj.name),
                dialog=self.dialog,
                task=task
            )
            gauge.display()


class ClusterVirtualMachineWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing virtual machines in a cluster

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A vim.ClusterComputeResource instance

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
                on_select_args=(self.agent, self.dialog, self.obj.parent.parent, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='Virtual Machines in cluster',
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
                text='No virtual machines found in cluster'
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
