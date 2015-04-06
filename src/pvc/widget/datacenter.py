"""
Datacenter Widgets

"""

import pyVmomi

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.event
import pvc.widget.hostsystem
import pvc.widget.menu
import pvc.widget.performance
import pvc.widget.virtualmachine

__all__ = [
    'DatacenterWidget', 'DatacenterActionWidget',
    'DatacenterClusterWidget',
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
                on_select=self.datacenter_host_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='VMs',
                description='Virtual Machines in datacenter',
                on_select=self.datacenter_vm_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastore',
                description='Datastores in datacenter',
                on_select=pvc.widget.common.datastore_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Networking',
                description='Networks in datacenter',
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
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select item from menu'
        )

        menu.display()

    def summary(self):
        """
        Datacenter general information

        """
        self.dialog.infobox(
            title=self.obj.name,
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
            title=self.obj.name,
            text='Datacenter general information'
        )

        form.display()

    def datacenter_host_menu(self):
        """
        Menu of hosts in the datacenter

        """
        self.dialog.infobox(
            title=self.obj.name,
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
                title=self.obj.name,
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
            title=self.obj.name,
            text='Select a host from the menu'
        )

        menu.display()

    def datacenter_vm_menu(self):
        """
        Menu of virtual machines in the datacenter

        """
        self.dialog.infobox(
            title=self.obj.name,
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
                title=self.obj.name,
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
            title=self.obj.name,
            text='Select a virtual machine from the menu'
        )

        menu.display()


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
                description='Remove datacenter'
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
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
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Create',
                description='Create new cluster in datacenter'
            ),
            pvc.widget.menu.MenuItem(
                tag='Remove',
                description='Remove cluster from datacenter'
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View clusters in datacenter'
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select a host action to be performed'
        )

        menu.display()
