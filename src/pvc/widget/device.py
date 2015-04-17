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
Widgets for managing virtual devices

"""

import pyVmomi

import pvc.widget.common
import pvc.widget.gauge
import pvc.widget.menu
import pvc.widget.radiolist

__all__ = [
    'BaseDeviceWidget', 'AddCdromDeviceWidget',
    'AddFloppyDeviceWidget', 'AddNetworkDeviceWidget',
]


class BaseDeviceWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Base device widget

        Args:
            agent          (VConnector): A VConnector instance
            dialog      (dialog.Dialog): A Dialog instance
            obj    (vim.VirtualMachine): A VirtualMachine managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.hardware = self.obj.config.hardware
        self.display()

    def display(self):
        """
        Override this method

        """
        pass

    def choose_controller(self, controller):
        """
        Prompts the user to select a virtual controller

        Args:
            controller (vim.VirtualController): Controller type to choose from

        Returns:
            A vim.VirtualController if a virtual controller has been
            selected, None otherwise

        """
        controllers = [d for d in self.hardware.device if isinstance(d, controller)]

        if not controllers:
            self.dialog.msgbox(
                title=self.title,
                text='No suitable controllers found'
            )
            return

        items = [
            pvc.widget.radiolist.RadioListItem(
                tag=d.deviceInfo.label
            ) for d in controllers
        ]

        radiolist = pvc.widget.radiolist.RadioList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select virtual controller'
        )

        code, tag = radiolist.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC) or not tag:
            return

        return [d for d in controllers if d.deviceInfo.label == tag].pop()

    def next_unit_number(self, controller):
        """
        Get the next unit number for a controller

        Args:
            controller (vim.VirtualController): A vim.VirtualController instance

        Returns:
            The next available unit number for the controller

        """
        used = [d.unitNumber for d in self.hardware.device if d.controllerKey == controller.key]

        next_unit_number = max(used) + 1 if used else 0

        return next_unit_number


class AddCdromDeviceWidget(BaseDeviceWidget):
    """
    Widget for adding new CD/DVD drives

    Extends:
        BaseDeviceWidget class

    Overrides:
        display() method

    """
    def display(self):
        controller = self.choose_controller(
            controller=pyVmomi.vim.VirtualIDEController
        )

        if not controller:
            return

        unit_number = self.next_unit_number(
            controller=controller
        )

        backing_info = self.select_backing()

        if not backing_info:
            return

        connect_info = pyVmomi.vim.VirtualDeviceConnectInfo(
            allowGuestControl=True,
            connected=False,
            startConnected=False
        )

        device = pyVmomi.vim.VirtualCdrom(
            backing=backing_info,
            connectable=connect_info,
            controllerKey=controller.key,
            key=-1,
            unitNumber=unit_number
        )

        device_change = pyVmomi.vim.VirtualDeviceConfigSpec(
            device=device,
            operation=pyVmomi.vim.VirtualDeviceConfigSpecOperation.add
        )

        spec = pyVmomi.vim.VirtualMachineConfigSpec(
            deviceChange=[device_change]
        )

        task = self.obj.ReconfigVM_Task(spec=spec)
        gauge = pvc.widget.gauge.TaskGauge(
            dialog=self.dialog,
            task=task,
            title=self.title,
            text='Adding CD/DVD drive ...'
        )

        gauge.display()

    def select_backing(self):
        """
        Prompts the user to select device backing

        Returns:
            A vim.VirtualDeviceDeviceBackingInfo instance on success,
            None otherwise

        """
        items = [
            pvc.widget.radiolist.RadioListItem(tag='Pass through'),
            pvc.widget.radiolist.RadioListItem(tag='ATAPI emulation'),
        ]

        radiolist = pvc.widget.radiolist.RadioList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select device backing'
        )

        code, tag = radiolist.display()
        if code in (self.dialog.CANCEL, self.dialog.ESC) or not tag:
            self.dialog.msgbox(
                title=self.title,
                text='Invalid device backing selected'
            )
            return

        if tag == 'Pass through':
            backing_info = pyVmomi.vim.VirtualCdromRemotePassthroughBackingInfo(
                deviceName='',
                useAutoDetect=False,
                exclusive=False
            )
        elif tag == 'ATAPI emulation':
            backing_info = pyVmomi.vim.VirtualCdromRemoteAtapiBackingInfo(
                deviceName='',
                useAutoDetect=False
            )

        return backing_info


class AddFloppyDeviceWidget(BaseDeviceWidget):
    """
    Widget for adding new floppy drives

    Extends:
        BaseDeviceWidget class

    Overrides:
        display() method

    """
    def display(self):
        controller = self.choose_controller(
            controller=pyVmomi.vim.VirtualSIOController
        )

        if not controller:
            return

        unit_number = self.next_unit_number(
            controller=controller
        )

        backing_info = pyVmomi.vim.VirtualFloppyRemoteDeviceBackingInfo(
            deviceName='',
            useAutoDetect=False
        )

        connect_info = pyVmomi.vim.VirtualDeviceConnectInfo(
            allowGuestControl=True,
            connected=False,
            startConnected=False
        )

        device = pyVmomi.vim.VirtualFloppy(
            backing=backing_info,
            connectable=connect_info,
            controllerKey=controller.key,
            key=-1,
            unitNumber=unit_number
        )

        device_change = pyVmomi.vim.VirtualDeviceConfigSpec(
            device=device,
            operation=pyVmomi.vim.VirtualDeviceConfigSpecOperation.add
        )

        spec = pyVmomi.vim.VirtualMachineConfigSpec(
            deviceChange=[device_change]
        )

        task = self.obj.ReconfigVM_Task(spec=spec)
        gauge = pvc.widget.gauge.TaskGauge(
            dialog=self.dialog,
            task=task,
            title=self.title,
            text='Adding floppy drive ...'
        )

        gauge.display()


class AddNetworkDeviceWidget(BaseDeviceWidget):
    """
    Widget for adding network devices

    Extends:
        BaseDeviceWidget class

    Overrides:
        display() method

    """
    def display(self):
        controller = self.choose_controller(
            controller=pyVmomi.vim.VirtualPCIController
        )

        if not controller:
            return

        unit_number = self.next_unit_number(
            controller=controller
        )

        adapter = self.select_ethernet_adapter()

        if not adapter:
            return

        network = pvc.widget.common.choose_network(
            agent=self.agent,
            dialog=self.dialog,
            obj=self.obj.runtime.host
        )

        if not network:
            return

        connect_info = pyVmomi.vim.VirtualDeviceConnectInfo(
            allowGuestControl=True,
            connected=True,
            startConnected=True
        )

        backing_info = pyVmomi.vim.VirtualEthernetCardNetworkBackingInfo(
            deviceName=network.name,
            useAutoDetect=False,
            network=network
        )

        device = adapter(
            backing=backing_info,
            connectable=connect_info,
            controllerKey=controller.key,
            key=-1,
            unitNumber=unit_number
        )

        device_change = pyVmomi.vim.VirtualDeviceConfigSpec(
            device=device,
            operation=pyVmomi.vim.VirtualDeviceConfigSpecOperation.add
        )

        spec = pyVmomi.vim.VirtualMachineConfigSpec(
            deviceChange=[device_change]
        )

        task = self.obj.ReconfigVM_Task(spec=spec)
        gauge = pvc.widget.gauge.TaskGauge(
            dialog=self.dialog,
            task=task,
            title=self.title,
            text='Adding ethernet adapter ...'
        )

        gauge.display()

    def select_ethernet_adapter(self):
        """
        Prompts the user to select an ethernet adapter

        Returns:
            A vim.VirtualEthernetAdapter type on success,
            None otherwise

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        # Get the OS descriptor which contains the list of
        # supported ethernet adapters on the virtual machine
        for descriptor in self.obj.environmentBrowser.QueryConfigOption().guestOSDescriptor:
            if hasattr(descriptor, 'supportedEthernetCard'):
                break
        else:
            self.dialog.msgbox(
                title=self.title,
                text='No supported ethernet adapters found'
            )
            return

        # The descriptor.supportedEthernetCard property
        # contains a list of vim.VirtualEthernetAdapter types.
        # In the radiolist we build below we use the
        # vim.VirtualEthernetAdapter.__name__ property to
        # present the user with a list of adapters to choose from
        items = [
            pvc.widget.radiolist.RadioListItem(
                tag=card.__name__.split('.')[-1].replace('Virtual', '').upper()
            ) for card in descriptor.supportedEthernetCard
        ]

        radiolist = pvc.widget.radiolist.RadioList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select virtual ethernet adapter'
        )

        code, tag = radiolist.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC) or not tag:
            return

        card_name = '{}{}'.format('vim.vm.device.Virtual', tag.title())

        return [c for c in descriptor.supportedEthernetCard if c.__name__ == card_name].pop()
