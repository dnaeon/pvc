"""
Virtual Machine Widgets

"""

import time

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.vnc
import pvc.widget.network
import pvc.widget.performance

from subprocess import Popen, PIPE

__all__ = ['VirtualMachineWidget']


class VirtualMachineWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Virtual Machine Widget

        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity

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
            ),
            pvc.widget.menu.MenuItem(
                tag='Rename',
                description='Rename Virtual Machine',
                on_select=pvc.widget.common.rename,
                on_select_args=(self.obj, self.dialog, 'New virtual machine name?')
            ),
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
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Guest OS',
                item=self.obj.config.guestFullName if self.obj.config.guestFullName else 'Unknown'
            ),
            pvc.widget.form.FormElement(
                label='VM Version',
                item=self.obj.config.version
            ),
            pvc.widget.form.FormElement(
                label='CPU',
                item='{} vCPU(s)'.format(self.obj.config.hardware.numCPU)
            ),
            pvc.widget.form.FormElement(
                label='Memory',
                item='{} MB'.format(self.obj.config.hardware.memoryMB)
            ),
            pvc.widget.form.FormElement(
                label='Memory Overhead',
                item='{} MB'.format(self.obj.summary.quickStats.consumedOverheadMemory)
            ),
            pvc.widget.form.FormElement(
                label='VMware Tools Status',
                item=self.obj.guest.toolsRunningStatus
            ),
            pvc.widget.form.FormElement(
                label='VMware Tools Version',
                item=self.obj.guest.toolsVersionStatus
            ),
            pvc.widget.form.FormElement(
                label='IP Address',
                item=self.obj.guest.ipAddress if self.obj.guest.ipAddress else 'Unknown'
            ),
            pvc.widget.form.FormElement(
                label='DNS Name',
                item=self.obj.guest.hostName if self.obj.guest.hostName else 'Unknown'
            ),
            pvc.widget.form.FormElement(
                label='State',
                item=self.obj.runtime.powerState
            ),
            pvc.widget.form.FormElement(
                label='Host',
                item=self.obj.runtime.host.name
            ),
            pvc.widget.form.FormElement(
                label='Template',
                item=str(self.obj.config.template)
            ),
            pvc.widget.form.FormElement(
                label='Folder',
                item=self.obj.parent.name
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
            text='Retrieving information ...'
        )

        provisioned_storage = self.obj.summary.storage.committed + \
                              self.obj.summary.storage.uncommitted

        elements = [
            pvc.widget.form.FormElement(
                label='Consumed Host CPU',
                item='{} MHz'.format(self.obj.summary.quickStats.overallCpuUsage)
            ),
            pvc.widget.form.FormElement(
                label='Consumed Host Memory',
                item='{} MB'.format(self.obj.summary.quickStats.hostMemoryUsage)
            ),
            pvc.widget.form.FormElement(
                label='Active Guest Memory',
                item='{} MB'.format(self.obj.summary.quickStats.guestMemoryUsage)
            ),
            pvc.widget.form.FormElement(
                label='Provisioned Storage',
                item=humanize.naturalsize(provisioned_storage, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Non-shared Storage',
                item=humanize.naturalsize(self.obj.summary.storage.unshared, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Used Storage',
                item=humanize.naturalsize(self.obj.summary.storage.committed, binary=True)
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
