"""
Docstring should go here

"""

import pyVmomi

from pvc.widget.menu import Menu, MenuItem
from pvc.widget.form import Form, FormElement

__all__ = ['VirtualMachineMainMenu']


class VirtualMachineMainMenu(object):
    def __init__(self, agent, dialog, obj):
        """
        Inventory menu

        Args:
            agent                 (VConnector): A VConnector instance
            dialog             (dialog.Dialog): A Dialog instance
            obj    (pyVmomi.vim.ManagedEntity): A VirtualMachine managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.menu()

    def menu(self):
        items = [
            MenuItem(
                tag='General',
                description='General information',
                on_select=self.general_info
            ),
            MenuItem(
                tag='Configuration',
                description='Virtual Machine settings'
            ),
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
            FormElement(label='Guest OS', item=properties.get('config.guestFullName', 'Unknown')),
            FormElement(label='VM Version', item=properties.get('config.version')),
            FormElement(label='CPU', item='{} vCPU(s)'.format(properties.get('config.hardware.numCPU'))),
            FormElement(label='Memory', item='{} MB'.format(properties.get('config.hardware.memoryMB'))),
            FormElement(label='Memory Overhead', item='{} MB'.format(properties.get('summary.quickStats.consumedOverheadMemory'))),
            FormElement(label='VMware Tools', item='{} ({})'.format(properties.get('guest.toolsRunningStatus'), properties.get('guest.toolsVersionStatus'))),
            FormElement(label='IP Address', item=properties.get('guest.ipAddress', 'Unknown')),
            FormElement(label='DNS Name', item=properties.get('guest.hostName', 'Unknown')),
            FormElement(label='State', item=properties.get('runtime.powerState')),
            FormElement(label='Host', item=self.obj.runtime.host.name),
        ]

        form = Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\nVirtual Machine General Information\n'
        )

        return form.display()
