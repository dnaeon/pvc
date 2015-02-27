"""
Docstring should go here

"""

import pyVmomi

from pvc.menu import Menu, MenuItem

__all__ = ['VirtualMachineMainMenu']


class VirtualMachineMainMenu(object):
    def __init__(self, obj, dialog):
        """
        Inventory menu

        Args:
            obj    (pyVmomi.vim.ManagedEntity): A VirtualMachine managed entity
            dialog                    (Dialog): A Dialog instance

        """
        self.obj = obj
        self.dialog = dialog
        self.menu()

    def menu(self):
        items = [
            MenuItem(
                tag='Summary',
                description='Virtual Machine Summary',
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
