"""
HostSystem Widgets

"""

import datetime

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.checklist
import pvc.widget.common
import pvc.widget.event
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.network
import pvc.widget.performance

__all__ = [
    'HostSystemWidget', 'HostSystemDatastoreWidget',
    'HostSystemAddNfsStorage', 'HostSystemUnmountStorage',
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
                description='Virtual Machines on this host',
                on_select=pvc.widget.common.virtual_machine_menu,
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
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select item from menu'
        )

        menu.display()

    def info(self):
        """
        General information

        """
        self.dialog.infobox(
            title=self.obj.name,
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
            title=self.obj.name,
            text='Host general information'
        )

        form.display()

    def resources(self):
        """
        Resource usage information

        """
        self.dialog.infobox(
            title=self.obj.name,
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
            title=self.obj.name,
            text='Host resource usage information'
        )

        form.display()


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
            title=self.obj.name,
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
            title='Add Storage',
            text='Select an action to be performed'
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
            title='Add Storage',
            text='Provide details of the remote NFS volume'
        )

        code, fields = form.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not all(fields.values()):
            self.dialog.msgbox(
                text='Invalid input provided'
            )
            return

        if fields['Read-Only'].lower() in ('yes', 'true'):
            access_mode = pyVmomi.vim.HostMountMode.readOnly
        else:
            access_mode = pyVmomi.vim.HostMountMode.readWrite

        self.dialog.infobox(
            title=self.obj.name,
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
        except Exception as e:
            self.dialog.msgbox(
                title='Error',
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
        self.display()

    def display(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        items = [
            pvc.widget.checklist.CheckListItem(
                tag=d.name,
                description=d.summary.accessible
            ) for d in self.obj.datastore
        ]

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
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
            title='Confirm Unmount',
            text=text.format('\n'.join(selected))
        )

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            return

        datastore_objects = [d for d in self.obj.datastore if d.name in selected]
        for datastore_obj in datastore_objects:
            self.dialog.infobox(
                text='Unmount datastore {} ...'.format(datastore_obj.name)
            )
            self.obj.configManager.datastoreSystem.RemoveDatastore(
                datastore=datastore_obj
            )
