"""
Virtual Machine Widgets

"""

import os
import time
import tarfile

import pyVmomi
import humanize
import requests

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.vnc
import pvc.widget.network
import pvc.widget.performance

from subprocess import Popen, PIPE

__all__ = [
    'VirtualMachineWidget',
    'VirtualMachineConsoleWidget',
    'VirtualMachinePowerWidget',
    'VirtualMachineExportWidget'
]


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
                tag='Actions',
                description='Available Actions',
                on_select=self.action_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Power',
                description='Virtual Machine Power Options',
                on_select=VirtualMachinePowerWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
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
                tag='Template',
                description='Template Actions',
                on_select=VirtualMachineTemplateWidget,
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
                on_select=VirtualMachineConsoleWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
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

    def action_menu(self):
        """
        Virtual Machine Actions Menu

        """
        items = [
            pvc.widget.menu.MenuItem(
                tag='Rename',
                description='Rename Virtual Machine',
                on_select=pvc.widget.common.rename,
                on_select_args=(self.obj, self.dialog, 'New virtual machine name?')
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            dialog=self.dialog,
            items=items
        )

        menu.display()

class VirtualMachinePowerWidget(object):
    """
    Virtual Machine Power Menu Widget

    """
    def __init__(self, agent, dialog, obj):
        """
        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
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


class VirtualMachineExportWidget(object):
    def __init__(self, agent, dialog, obj, create_ova):
        """
        Virtual Machine Export Widget

        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity
            create_ova           (bool): If True then export VM into a single OVA file
                                         Otherwise create a folder of files (OVF)

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.create_ova = create_ova
        self.display()

    def display(self):
        if self.obj.runtime.powerState != pyVmomi.vim.VirtualMachinePowerState.poweredOff:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Virtual Machine must be powered off in order to be exported'
            )
            return

        code, path = self.dialog.dselect(
            title='Directory to save OVF template',
            filepath='',
            width=60
        )

        path = os.path.join(path, self.obj.name)

        if code in (self.dialog.ESC, self.dialog.CANCEL):
            self.dialog.msgbox(
                title=self.obj.name,
                text='No destination directory specified'
            )
            return

        if not os.path.exists(path):
            os.makedirs(path)

        self.export_ovf_template(path=path)

    def export_ovf_template(self, path):
        """
        Exports a Virtual Machine into OVF/OVA template

        Args:
            path (str): Directory to save the OVF/OVA template

        """
        # TODO: Perform a dry-run and see if creating the
        #       OVF descriptor succeeds and then proceed with
        #       downloading the actual VMDK files

        self.dialog.infobox(
            title=self.obj.name,
            text='Initializing OVF export ...',
            width=60
        )

        lease = self.obj.ExportVm()

        while True:
            if lease.state == pyVmomi.vim.HttpNfcLeaseState.initializing:
                lease.HttpNfcLeaseProgress(percent=0)
            elif lease.state == pyVmomi.vim.HttpNfcLeaseState.error:
                self.dialog.msgbox(
                    title=self.obj.name,
                    text=lease.error.msg
                )
                lease.HttpNfcLeaseAbort()
                return
            elif lease.state == pyVmomi.vim.HttpNfcLeaseState.ready:
                break
            time.sleep(0.5)

        percent = 0
        total_transfered_bytes = 0
        manifest = []
        ovf_files = []
        exported_disks = {}

        self.dialog.gauge_start(
            title='Exporting OVF template - {}'.format(self.obj.name)
        )

        for url in lease.info.deviceUrl:
            if not url.disk: # skip non-vmdk disks
                continue

            self.dialog.gauge_update(
                percent=percent,
                text='\nExporting {} ...\n'.format(url.targetId),
                update_text=True
            )

            if manifest:
                total_transfered_bytes = sum([m.capacity for m in manifest])

            disk_transfered_bytes = 0
            disk_file = os.path.join(path, '{}-{}'.format(self.obj.name, url.targetId))
            r = requests.get(url.url, verify=False, stream=True)

            with open(disk_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512*1024):
                    if chunk:
                        disk_transfered_bytes += len(chunk)
                        percent = round(
                            (total_transfered_bytes + disk_transfered_bytes) / 1024 /
                            lease.info.totalDiskCapacityInKB * 100
                        )
                        self.dialog.gauge_update(percent=percent)
                        lease.HttpNfcLeaseProgress(percent=percent)
                        f.write(chunk)

            m = [m for m in lease.HttpNfcLeaseGetManifest() if m.key == url.key].pop()
            manifest.append(m)

            of = pyVmomi.vim.OvfManager.OvfFile(
                capacity=m.capacity,
                deviceId=m.key,
                path=os.path.basename(disk_file),
                populatedSize=m.populatedSize,
                size=disk_transfered_bytes,
            )
            ovf_files.append(of)

            exported_disks[url.key] = url.targetId
            total_transfered_bytes = sum([m.capacity for m in manifest])
            percent = round(
                total_transfered_bytes / 1024 / lease.info.totalDiskCapacityInKB * 100
            )
            self.dialog.gauge_update(percent)
            lease.HttpNfcLeaseProgress(percent=percent)

        # Create OVF manifest and descriptor files
        self.dialog.gauge_stop()
        self.create_manifest_file(
            path=path,
            manifest=manifest,
            disks=exported_disks
        )

        self.create_ovf_descriptor(
            path=path,
            ovf_files=ovf_files
        )

        lease.HttpNfcLeaseComplete()

        if self.create_ova:
            self.create_ova_file(
                path=path,
                disks=exported_disks.values()
            )

        self.dialog.msgbox(
            title=self.obj.name,
            text='\nExport successful. Files saved in:\n\n{}\n'.format(path),
            width=60
        )

    def create_manifest_file(self, path, manifest, disks):
        """
        Creates the OVF manifest file

        Args:
            path      (str): Path to the exported disks
            manifest (list): A list of vim.HttpNfcLease.ManifestEntry instances
            disks    (dict): A mapping of the disk keys and target ids

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Creating OVF manifest ...'
        )

        with open(os.path.join(path, '{}.mf'.format(self.obj.name)), 'w') as f:
            for entry in manifest:
                f.write('SHA1({}-{})= {}\n'.format(
                    self.obj.name,
                    disks[entry.key],
                    entry.sha1)
                )

    def create_ovf_descriptor(self, path, ovf_files):
        """
        Creates the OVF descriptor file

        Args:
            path       (str): Path to the exported disks
            ovf_files (list): A list of vim.OvfManager.OvfFile instances

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Creating OVF descriptor ...'
        )

        cdp = pyVmomi.vim.OvfManager.CreateDescriptorParams(
            ovfFiles=ovf_files
        )

        dr = self.agent.si.content.ovfManager.CreateDescriptor(
            obj=self.obj,
            cdp=cdp
        )

        if dr.warning:
            self.dialog.msgbox(
                title='Warning - {}'.format(self.obj.name),
                text=str(dr.warning),
                width=60
            )

        if dr.error:
            self.dialog.msgbox(
                title='Error - {}'.format(self.obj.name),
                text=str(dr.error),
                width=60
            )

        with open(os.path.join(path, '{}.ovf'.format(self.obj.name)), 'w') as f:
            f.write(dr.ovfDescriptor)

    def create_ova_file(self, path, disks):
        """
        Creates a single OVA file of the exported VM

        Args:
            path   (str): Path to the exported disks
            disks (list): A list of the downloaded disks

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Creating OVA file ...',
            width=60
        )

        old_cwd = os.getcwd()
        os.chdir(path)

        ova = tarfile.open('{}.ova'.format(self.obj.name), 'w')

        # Add descriptor and manifest files first
        descriptor = '{}.ovf'.format(self.obj.name)
        manifest = '{}.mf'.format(self.obj.name)
        ova.add(descriptor)
        ova.add(manifest)

        # Now add the VMDK disks
        for disk in disks:
            ova.add('{}-{}'.format(self.obj.name, disk))

        ova.close()

        # Cleanup disks, manifest and descriptor files
        os.unlink(manifest)
        os.unlink(descriptor)
        for disk in disks:
            os.unlink('{}-{}'.format(self.obj.name, disk))

        os.chdir(old_cwd)


class VirtualMachineConsoleWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Virtual Machine Console Widget

        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
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


class VirtualMachineTemplateWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Virtual Machine Template Widget

        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Export OVA',
                description='Single file (OVA)',
                on_select=VirtualMachineExportWidget,
                on_select_args=(self.agent, self.dialog, self.obj, True)
            ),
            pvc.widget.menu.MenuItem(
                tag='Export OVF',
                description='Directory of files (OVF)',
                on_select=VirtualMachineExportWidget,
                on_select_args=(self.agent, self.dialog, self.obj, False)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            dialog=self.dialog,
            items=items
        )

        menu.display()
