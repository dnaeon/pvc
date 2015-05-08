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
HostSystem Widgets

"""

import datetime

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.checklist
import pvc.widget.common
import pvc.widget.debug
import pvc.widget.event
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.network
import pvc.widget.performance
import pvc.widget.virtualmachine

__all__ = [
    'HostSystemWidget', 'HostSystemDatastoreWidget',
    'HostSystemAddNfsStorage', 'HostSystemUnmountStorage',
    'HostSystemVirtualMachineWidget', 'HostSystemServiceWidget',
]


class HostSystemWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        HostSystem Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='General',
                description='General information',
                on_select=self.info
            ),
            pvc.widget.menu.MenuItem(
                tag='Resources',
                description='Resource usage information',
                on_select=self.resources
            ),
            pvc.widget.menu.MenuItem(
                tag='Virtual Machines',
                description='Manage Virtual Machines',
                on_select=HostSystemVirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Networks',
                description='Host Networks',
                on_select=pvc.widget.common.network_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastores',
                description='Manage datastores on this host',
                on_select=HostSystemDatastoreWidget,
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
                tag='Services',
                description='Manage Services',
                on_select=pvc.widget.common.host_service_menu,
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
            text='Select an action to be performed'
        )

        menu.display()

    def info(self):
        """
        General information

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='State',
                item=self.obj.runtime.connectionState
            ),
            pvc.widget.form.FormElement(
                label='Type',
                item=self.obj.config.product.fullName,
            ),
            pvc.widget.form.FormElement(
                label='Vendor',
                item=self.obj.hardware.systemInfo.vendor
            ),
            pvc.widget.form.FormElement(
                label='Model',
                item=self.obj.hardware.systemInfo.model
            ),
            pvc.widget.form.FormElement(
                label='Memory Size',
                item=humanize.naturalsize(self.obj.hardware.memorySize, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='CPU Packages',
                item=str(self.obj.hardware.cpuInfo.numCpuPackages)
            ),
            pvc.widget.form.FormElement(
                label='CPU Cores',
                item=str(self.obj.hardware.cpuInfo.numCpuCores)
            ),
            pvc.widget.form.FormElement(
                label='CPU Threads',
                item=str(self.obj.hardware.cpuInfo.numCpuThreads)
            ),
            pvc.widget.form.FormElement(
                label='Uptime',
                item=str(datetime.timedelta(seconds=self.obj.summary.quickStats.uptime))
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Host general information'
        )

        form.display()

    def resources(self):
        """
        Resource usage information

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='CPU Usage',
                item='{} MHz'.format(self.obj.summary.quickStats.overallCpuUsage)
            ),
            pvc.widget.form.FormElement(
                label='Memory Usage',
                item='{} MB'.format(self.obj.summary.quickStats.overallMemoryUsage)
            ),
            pvc.widget.form.FormElement(
                label='CPU Fairness',
                item='{} MHz'.format(self.obj.summary.quickStats.distributedCpuFairness)
            ),
            pvc.widget.form.FormElement(
                label='Memory Fairness',
                item='{} MB'.format(self.obj.summary.quickStats.distributedMemoryFairness)
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Host resource usage information'
        )

        form.display()


class HostSystemVirtualMachineWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing Virtual Machines on a HostSystem

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

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
                on_select_args=(self.agent, self.dialog, self.obj.parent.parent.parent, self.obj.parent, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View Virtual Machines on host',
                on_select=pvc.widget.common.virtual_machine_menu,
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


class HostSystemDatastoreWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for managing datastores on a HostSystem

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

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
                description='Create new datastore',
                on_select=self.create_datastore
            ),
            pvc.widget.menu.MenuItem(
                tag='Unmount',
                description='Unmount datastores',
                on_select=HostSystemUnmountStorage,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View datastores',
                on_select=pvc.widget.common.datastore_menu,
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

    def create_datastore(self):
        """
        Create new datastore menu

        """
        items = [
            pvc.widget.menu.MenuItem(
                tag='NFS',
                description='Mount NFS volume',
                on_select=HostSystemAddNfsStorage,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Add storage',
        )

        menu.display()


class HostSystemAddNfsStorage(object):
    def __init__(self, agent, dialog, obj):
        """
        Create new datastore using a NFS volume

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        elements = [
            pvc.widget.form.FormElement(label='Server'),
            pvc.widget.form.FormElement(label='Path', item='/vol0/datastore'),
            pvc.widget.form.FormElement(label='Read-Only', item='False'),
            pvc.widget.form.FormElement(label='Datastore Name'),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Provide details of the remote NFS volume'
        )

        code, fields = form.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not all(fields.values()):
            self.dialog.msgbox(
                title=self.title,
                text='Error, invalid input provided'
            )
            return

        if fields['Read-Only'].lower() in ('yes', 'true'):
            access_mode = pyVmomi.vim.HostMountMode.readOnly
        else:
            access_mode = pyVmomi.vim.HostMountMode.readWrite

        self.dialog.infobox(
            title=self.title,
            text='Creating datastore {} ...'.format(fields['Datastore Name'])
        )

        spec = pyVmomi.vim.HostNasVolumeSpec(
            accessMode=access_mode,
            localPath=fields['Datastore Name'],
            remoteHost=fields['Server'],
            remotePath=fields['Path']
        )

        try:
            self.obj.configManager.datastoreSystem.CreateNasDatastore(
                spec=spec
            )
        except pyVmomi.vim.MethodFault as e:
            self.dialog.msgbox(
                title=self.title,
                text=e.msg
            )


class HostSystemUnmountStorage(object):
    def __init__(self, agent, dialog, obj):
        """
        Widget for unmount datastores from host

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        if not self.obj.datastore:
            self.dialog.msgbox(
                title=self.title,
                text='There are no datastores mounted on this host'
            )
            return

        items = [
            pvc.widget.checklist.CheckListItem(
                tag=d.name,
                description='Accessible' if d.summary.accessible else 'Not Accessible',
            ) for d in self.obj.datastore
        ]

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select datastore(s) to be unmounted'
        )

        checklist.display()
        selected = checklist.selected()

        if not selected:
            return

        text = (
            'The following datastore(s) will be unmounted.'
            '\n\n{}\n\n'
            'Unmount datastore(s) from host?\n'
        )

        code = self.dialog.yesno(
            title=self.title,
            text=text.format('\n'.join(selected))
        )

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        datastore_objects = [d for d in self.obj.datastore if d.name in selected]
        for datastore_obj in datastore_objects:
            self.dialog.infobox(
                title=self.title,
                text='Unmount datastore {} ...'.format(datastore_obj.name)
            )
            self.obj.configManager.datastoreSystem.RemoveDatastore(
                datastore=datastore_obj
            )


class HostSystemServiceWidget(object):
    def __init__(self, agent, dialog, obj, service):
        """
        Widget for managing services on a HostSystem

        Args:
            agent        (VConnector): A VConnector instance
            dialog    (dialog.Dialog): A Dialog instance
            obj      (vim.HostSystem): A HostSystem managed entity
            service (vim.HostService): A HostService instance

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.service = service
        self.service_system = self.obj.configManager.serviceSystem
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Info',
                description='View Service Info',
                on_select=self.info
            ),
            pvc.widget.menu.MenuItem(
                tag='Start',
                description='Start Service',
                on_select=self.start
            ),
            pvc.widget.menu.MenuItem(
                tag='Stop',
                description='Stop Service',
                on_select=self.stop
            ),
            pvc.widget.menu.MenuItem(
                tag='Restart',
                description='Restart Service',
                on_select=self.restart
            ),
            pvc.widget.menu.MenuItem(
                tag='Uninstall',
                description='Uninstall Service',
                on_select=self.uninstall
            ),
            pvc.widget.menu.MenuItem(
                tag='Policy',
                description='Update Service Policy',
                on_select=self.update_policy
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()

    def info(self):
        """
        Display info about a service

        """
        elements = [
            pvc.widget.form.FormElement(
                label='Service',
                item=self.service.key
            ),
            pvc.widget.form.FormElement(
                label='Description',
                item=self.service.label
            ),
            pvc.widget.form.FormElement(
                label='Running',
                item=str(self.service.running)
            ),
            pvc.widget.form.FormElement(
                label='Policy',
                item=self.service.policy
            ),
            pvc.widget.form.FormElement(
                label='Required',
                item=str(self.service.required)
            ),
            pvc.widget.form.FormElement(
                label='Uninstallable',
                item=str(self.service.uninstallable)
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Service information'
        )

        form.display()

    def start(self):
        """
        Starts a service

        """
        self.dialog.infobox(
            title=self.title,
            text='Starting service {} ...'.format(self.service.label)
        )

        self.service_system.StartService(id=self.service.key)

    def stop(self):
        """
        Stops a service

        """
        self.dialog.infobox(
            title=self.title,
            text='Stopping service {} ...'.format(self.service.label)
        )

        self.service_system.StopService(id=self.service.key)

    def restart(self):
        """
        Restarts a service

        """
        self.dialog.infobox(
            title=self.title,
            text='Restarting service {} ...'.format(self.service.label)
        )

        self.service_system.RestartService(id=self.service.key)

    def uninstall(self):
        """"
        Uninstalls a service

        """
        self.dialog.infobox(
            title=self.title,
            text='Uninstall service {} ...'.format(self.service.label)
        )

        try:
            self.service_system.UninstallService(id=self.service.key)
        except pyVmomi.vim.MethodFault as e:
            self.dialog.msgbox(
                title=self.title,
                text=e.msg
            )

    def update_policy(self):
        """
        Updates the activation policy of a service

        """
        items = [
            pvc.widget.menu.MenuItem(
                tag='On',
                description='Enable service at boot-time',
                on_select=lambda x: x,
                on_select_args=(pyVmomi.vim.HostServicePolicy.on,)
            ),
            pvc.widget.menu.MenuItem(
                tag='Off',
                description='Disable service at boot-time',
                on_select=lambda x: x,
                on_select_args=(pyVmomi.vim.HostServicePolicy.off,)
            ),
            pvc.widget.menu.MenuItem(
                tag='Automatic',
                description='Start service only if it has open ports',
                on_select=lambda x: x,
                on_select_args=(pyVmomi.vim.HostServicePolicy.automatic,)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            return_selected=True,
            title=self.title,
            text='Select service activation policy'
        )

        item = menu.display()

        if not isinstance(item, pvc.widget.menu.MenuItem):
            return

        policy = item.selected()

        self.dialog.infobox(
            title=self.title,
            text='Updating policy for service {} ...'.format(self.service.label)
        )

        self.service_system.UpdateServicePolicy(
            id=self.service.key,
            policy=policy
        )
