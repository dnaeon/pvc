"""
Docstring should go here

"""

import pyVmomi

from pvc.widget.alarm import AlarmWidget
from pvc.widget.menu import Menu, MenuItem
from pvc.widget.form import Form, FormElement
from pvc.widget.gauge import TaskGauge
from pvc.widget.vnc import VncWidget

__all__ = ['VirtualMachineWidget']


class VirtualMachineWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Virtual Machine Widget

        Args:
            agent                 (VConnector): A VConnector instance
            dialog             (dialog.Dialog): A Dialog instance
            obj    (pyVmomi.vim.ManagedEntity): A VirtualMachine managed entity

        """
        if not isinstance(obj, pyVmomi.vim.VirtualMachine):
            raise TypeError('Need a vim.VirtualMachine instance')

        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            MenuItem(
                tag='General',
                description='General information',
                on_select=self.general_info
            ),
            MenuItem(
                tag='Resources',
                description='Resources usage information ',
                on_select=self.resources_info
            ),
            MenuItem(
                tag='Power',
                description='Virtual Machine Power Options',
                on_select=self.power_menu,
            ),
            MenuItem(
                tag='Configuration',
                description='Virtual Machine settings'
            ),
            MenuItem(
                tag='Tasks & Events',
                description='View Tasks & Events'
            ),
            MenuItem(
                tag='Alarms',
                description='View triggered alarms',
                on_select=AlarmWidget,
                on_select_args=(self.obj.name, self.agent, self.dialog, self.obj.triggeredAlarmState)
            ),
            MenuItem(
                tag='Console',
                description='Launch Console',
                on_select=self.console_menu
            )
        ]

        menu = Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def general_info(self):
        """
        Virtual Machine general information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving general information ...'
        )

        view = self.agent.get_list_view([self.obj])
        data = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.VirtualMachine,
            path_set=[
                'config.guestFullName',
                'guest.hostName',
                'guest.ipAddress',
                'guest.toolsRunningStatus',
                'guest.toolsVersionStatus',
                'config.version',
                'config.hardware.numCPU',
                'config.hardware.memoryMB',
                'summary.quickStats.consumedOverheadMemory',
                'runtime.powerState',
            ]
        )
        view.DestroyView()
        properties = data.pop()

        elements = [
            FormElement(
                label='Guest OS',
                item=properties.get('config.guestFullName', 'Unknown')
            ),
            FormElement(
                label='VM Version',
                item=properties.get('config.version')
            ),
            FormElement(
                label='CPU',
                item='{} vCPU(s)'.format(properties.get('config.hardware.numCPU'))
            ),
            FormElement(
                label='Memory',
                item='{} MB'.format(properties.get('config.hardware.memoryMB'))
            ),
            FormElement(
                label='Memory Overhead',
                item='{} MB'.format(properties.get('summary.quickStats.consumedOverheadMemory'))
            ),
            FormElement(
                label='VMware Tools',
                item='{} ({})'.format(properties.get('guest.toolsRunningStatus'), properties.get('guest.toolsVersionStatus'))
            ),
            FormElement(
                label='IP Address',
                item=properties.get('guest.ipAddress', 'Unknown')
            ),
            FormElement(
                label='DNS Name',
                item=properties.get('guest.hostName', 'Unknown')
            ),
            FormElement(
                label='State',
                item=properties.get('runtime.powerState')
            ),
            FormElement(
                label='Host',
                item=self.obj.runtime.host.name
            ),
        ]

        form = Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\nVirtual Machine General Information\n'
        )

        return form.display()

    def resources_info(self):
        """
        Resources usage information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving resources usage information ...'
        )

        view = self.agent.get_list_view([self.obj])
        data = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.VirtualMachine,
            path_set=[
                'summary.quickStats.overallCpuUsage',
                'summary.quickStats.hostMemoryUsage',
                'summary.quickStats.guestMemoryUsage',
                'summary.storage.committed',
                'summary.storage.uncommitted',
                'summary.storage.unshared',
            ]
        )
        view.DestroyView()
        properties = data.pop()

        # Convert storage information into GB first
        properties['summary.storage.committed'] /= 1073741824
        properties['summary.storage.unshared'] /= 1073741824
        properties['summary.storage.uncommitted'] /= 1073741824

        elements = [
            FormElement(
                label='Consumed Host CPU',
                item='{} MHz'.format(properties.get('summary.quickStats.overallCpuUsage'))
            ),
            FormElement(
                label='Consumed Host Memory',
                item='{} MB'.format(properties.get('summary.quickStats.hostMemoryUsage'))
            ),
            FormElement(
                label='Active Guest Memory',
                item='{} MB'.format(properties.get('summary.quickStats.guestMemoryUsage'))
            ),
            FormElement(
                label='Provisioned Storage',
                item='{} GB'.format(round(properties.get('summary.storage.committed') + properties.get('summary.storage.uncommitted'), 2))
            ),
            FormElement(
                label='Non-shared Storage',
                item='{} GB'.format(round(properties.get('summary.storage.unshared'), 2))
            ),
            FormElement(
                label='Used Storage',
                item='{} GB'.format(round(properties.get('summary.storage.committed'), 2))
            ),
        ]

        form = Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\nVirtual Machine Resources Usage Information\n'
        )

        return form.display()

    def power_menu(self):
        """
        Virtual Machine Power menu

        """
        items = [
            MenuItem(
                tag='Power On',
                description='Power On Virtual Machine',
                on_select=self.power_on
            ),
            MenuItem(
                tag='Power Off',
                description='Power Off Virtual Machine Off ',
                on_select=self.power_off
            ),
            MenuItem(
                tag='Suspend',
                description='Suspend Virtual Machine',
                on_select=self.suspend,
            ),
            MenuItem(
                tag='Reset',
                description='Reset Virtual Machine',
                on_select=self.reset
            ),
            MenuItem(
                tag='Shutdown',
                description='Shutdown Guest System',
                on_select=self.shutdown
            ),
            MenuItem(
                tag='Reboot',
                description='Reboot Guest System',
                on_select=self.reboot
            ),
        ]

        menu = Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def console_menu(self):
        """
        Virtual Machine Console Menu

        """
        items = [
            MenuItem(
                tag='VNC',
                description='Launch VNC Console',
                on_select=VncWidget,
                on_select_args=(self.dialog, self.obj)
            ),
            MenuItem(
                tag='VMRC',
                description='Launch VMRC Console '
            ),
        ]

        menu = Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def power_on(self):
        """
        Power on the virtual machine

        """
        if self.obj.runtime.powerState == pyVmomi.vim.VirtualMachinePowerState.poweredOn:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is already powered on.'
            )
            return

        task = self.obj.PowerOn()
        gauge = TaskGauge(
            title=self.obj.name,
            text='Powering On Virtual Machine',
            dialog=self.dialog,
            task=task
        )
        gauge.display()

    def power_off(self):
        """
        Power off the virtual machine

        """
        if self.obj.runtime.powerState == pyVmomi.vim.VirtualMachinePowerState.poweredOff:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is already powered off.'
            )
            return

        task = self.obj.PowerOff()
        gauge = TaskGauge(
            title=self.obj.name,
            text='Powering Off Virtual Machine',
            dialog=self.dialog,
            task=task
        )
        gauge.display()

    def suspend(self):
        """
        Suspend the virtual machine

        """
        if self.obj.runtime.powerState != pyVmomi.vim.VirtualMachinePowerState.poweredOn:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is not powered on, cannot suspend.'
            )
            return

        task = self.obj.Suspend()
        gauge = TaskGauge(
            title=self.obj.name,
            text='Suspending Virtual Machine',
            dialog=self.dialog,
            task=task
        )
        gauge.display()

    def reset(self):
        """
        Reset the virtual machine

        """
        if self.obj.runtime.powerState != pyVmomi.vim.VirtualMachinePowerState.poweredOn:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is not powered on, cannot reset.'
            )
            return

        task = self.obj.Reset()
        gauge = TaskGauge(
            title=self.obj.name,
            text='Resetting Virtual Machine',
            dialog=self.dialog,
            task=task
        )
        gauge.display()

    def shutdown(self):
        """
        Shutdown the virtual machine

        For a proper guest shutdown we need VMware Tools running

        """
        if self.obj.runtime.powerState != pyVmomi.vim.VirtualMachinePowerState.poweredOn:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is not powered on, cannot shutdown.'
            )
            return

        if self.obj.guest.toolsRunningStatus != pyVmomi.vim.VirtualMachineToolsRunningStatus.guestToolsRunning:
            self.dialog.msgbox(
                title=self.obj.name,
                text='VMware Tools is not running, cannot shutdown system'
            )
            return

        self.dialog.infobox(
            title=self.obj.name,
            text='Shutting down guest system ...'
        )
        task = self.obj.ShutdownGuest()

    def reboot(self):
        """
        Reboot the virtual machine

        For a proper guest reboot we need VMware Tools running

        """
        if self.obj.runtime.powerState != pyVmomi.vim.VirtualMachinePowerState.poweredOn:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine is not powered on, cannot reboot.'
            )
            return

        if self.obj.guest.toolsRunningStatus != pyVmomi.vim.VirtualMachineToolsRunningStatus.guestToolsRunning:
            self.dialog.msgbox(
                title=self.obj.name,
                text='VMware Tools is not running, cannot reboot system'
            )
            return

        self.dialog.infobox(
            title=self.obj.name,
            text='Rebooting guest system ...'
        )
        task = self.obj.RebootGuest()
