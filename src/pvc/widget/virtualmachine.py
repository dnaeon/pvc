"""
Docstring should go here

"""

import time

import pyVmomi
import pvc.widget.alarm
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.vnc
import pvc.widget.network

from subprocess import Popen, PIPE

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
            pvc.widget.menu.MenuItem(
                tag='General',
                description='General information',
                on_select=self.general_info
            ),
            pvc.widget.menu.MenuItem(
                tag='Resources',
                description='Resources usage information ',
                on_select=self.resources_info
            ),
            pvc.widget.menu.MenuItem(
                tag='Power',
                description='Virtual Machine Power Options',
                on_select=self.power_menu,
            ),
            pvc.widget.menu.MenuItem(
                tag='Configuration',
                description='Virtual Machine settings'
            ),
            pvc.widget.menu.MenuItem(
                tag='Network',
                description='Virtual Machine Networking',
                on_select=self.network_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Tasks & Events',
                description='View Tasks & Events'
            ),
            pvc.widget.menu.MenuItem(
                tag='Alarms',
                description='View triggered alarms',
                on_select=pvc.widget.alarm.AlarmWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Console',
                description='Launch Console',
                on_select=self.console_menu
            )
        ]

        menu = pvc.widget.menu.Menu(
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

        # TODO: Do we want a property collector for a single object?
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
                'config.template',
                'summary.quickStats.consumedOverheadMemory',
                'runtime.powerState',
            ]
        )
        view.DestroyView()
        properties = data.pop()

        elements = [
            pvc.widget.form.FormElement(
                label='Guest OS',
                item=properties.get('config.guestFullName', 'Unknown')
            ),
            pvc.widget.form.FormElement(
                label='VM Version',
                item=properties.get('config.version')
            ),
            pvc.widget.form.FormElement(
                label='CPU',
                item='{} vCPU(s)'.format(properties.get('config.hardware.numCPU'))
            ),
            pvc.widget.form.FormElement(
                label='Memory',
                item='{} MB'.format(properties.get('config.hardware.memoryMB'))
            ),
            pvc.widget.form.FormElement(
                label='Memory Overhead',
                item='{} MB'.format(properties.get('summary.quickStats.consumedOverheadMemory'))
            ),
            pvc.widget.form.FormElement(
                label='VMware Tools',
                item='{} ({})'.format(properties.get('guest.toolsRunningStatus'), properties.get('guest.toolsVersionStatus'))
            ),
            pvc.widget.form.FormElement(
                label='IP Address',
                item=properties.get('guest.ipAddress', 'Unknown')
            ),
            pvc.widget.form.FormElement(
                label='DNS Name',
                item=properties.get('guest.hostName', 'Unknown')
            ),
            pvc.widget.form.FormElement(
                label='State',
                item=properties.get('runtime.powerState')
            ),
            pvc.widget.form.FormElement(
                label='Host',
                item=self.obj.runtime.host.name
            ),
            pvc.widget.form.FormElement(
                label='Template',
                item=str(properties['config.template'])
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\nVirtual Machine General Information\n'
        )

        form.display()

    def resources_info(self):
        """
        Resources usage information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving resources usage information ...'
        )

        # TODO: Do we want a property collector for a single object?
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
            pvc.widget.form.FormElement(
                label='Consumed Host CPU',
                item='{} MHz'.format(properties.get('summary.quickStats.overallCpuUsage'))
            ),
            pvc.widget.form.FormElement(
                label='Consumed Host Memory',
                item='{} MB'.format(properties.get('summary.quickStats.hostMemoryUsage'))
            ),
            pvc.widget.form.FormElement(
                label='Active Guest Memory',
                item='{} MB'.format(properties.get('summary.quickStats.guestMemoryUsage'))
            ),
            pvc.widget.form.FormElement(
                label='Provisioned Storage',
                item='{} GB'.format(round(properties.get('summary.storage.committed') + properties.get('summary.storage.uncommitted'), 2))
            ),
            pvc.widget.form.FormElement(
                label='Non-shared Storage',
                item='{} GB'.format(round(properties.get('summary.storage.unshared'), 2))
            ),
            pvc.widget.form.FormElement(
                label='Used Storage',
                item='{} GB'.format(round(properties.get('summary.storage.committed'), 2))
            ),
        ]

        form = pvc.widget.form.Form(
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
            pvc.widget.menu.MenuItem(
                tag='Power On',
                description='Power On Virtual Machine',
                on_select=self.power_on
            ),
            pvc.widget.menu.MenuItem(
                tag='Power Off',
                description='Power Off Virtual Machine Off ',
                on_select=self.power_off
            ),
            pvc.widget.menu.MenuItem(
                tag='Suspend',
                description='Suspend Virtual Machine',
                on_select=self.suspend,
            ),
            pvc.widget.menu.MenuItem(
                tag='Reset',
                description='Reset Virtual Machine',
                on_select=self.reset
            ),
            pvc.widget.menu.MenuItem(
                tag='Shutdown',
                description='Shutdown Guest System',
                on_select=self.shutdown
            ),
            pvc.widget.menu.MenuItem(
                tag='Reboot',
                description='Reboot Guest System',
                on_select=self.reboot
            ),
        ]

        menu = pvc.widget.menu.Menu(
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
            pvc.widget.menu.MenuItem(
                tag='VNC',
                description='Launch VNC Console',
                on_select=pvc.widget.vnc.VncWidget,
                on_select_args=(self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='VMware Player',
                description='Launch VMware Player Console',
                on_select=self.vmplayer_console,
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def network_menu(self):
        """
        Virtual Machine Network Menu

        """
        items = [
            pvc.widget.menu.MenuItem(
                tag=network.name,
                description='Accessible' if network.summary.accessible else 'Not Accessible',
                on_select=pvc.widget.network.NetworkWidget,
                on_select_args=(self.agent, self.dialog, network)
            ) for network in self.obj.network
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text='Virtual Machine Networks',
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
        gauge = pvc.widget.gauge.TaskGauge(
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
        gauge = pvc.widget.gauge.TaskGauge(
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
        gauge = pvc.widget.gauge.TaskGauge(
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
        gauge = pvc.widget.gauge.TaskGauge(
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
        self.obj.ShutdownGuest()

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
        self.obj.RebootGuest()

    def vmplayer_console(self):
        """
        Launch a VMware Player console to the Virtual Machine

        In order to establish a remote console session to the
        Virtual Machine we run VMware Player this way:

            $ vmplayer -h <hostname> -p <ticket> -M <managed-object-id>

        Where <ticket> is an acquired ticket as returned by a
        previous call to AcquireCloneTicket().

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Launching console ...'
        )

        ticket = self.agent.si.content.sessionManager.AcquireCloneTicket()

        try:
            p = Popen(
                args=['vmplayer', '-h', self.agent.host, '-p', ticket, '-M', self.obj._moId],
                stdout=PIPE,
                stderr=PIPE
            )
        except OSError as e:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Cannot launch console: \n{}\n'.format(e)
            )
            return

        # Give it some time to start up the console
        time.sleep(3)
