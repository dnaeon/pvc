"""
Docstring should go here

"""

import pyVmomi

import pvc.widget.menu
import pvc.widget.datastore
import pvc.widget.network
import pvc.widget.virtualmachine

__all__ = ['InventoryWidget']


class InventoryWidget(object):
    def __init__(self, agent, dialog):
        """
        Inventory widget

        Args:
            agent (VConnector): A VConnector instance
            dialog    (Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Hosts and Clusters',
                description='Manage hosts and clusters',
            ),
            pvc.widget.menu.MenuItem(
                tag='VMs and Templates',
                description='Manage VMs and templates',
                on_select=self.virtual_machine_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastores',
                description='Manage Datastores and Datastore Clusters',
                on_select=self.datastore_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Networking',
                description='Manage Networking',
                on_select=self.network_menu
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title='Inventory Menu',
            text='Select an item from the inventory',
            items=items,
            dialog=self.dialog,
            width=70,
        )
        menu.display()

    def datastore_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        view = self.agent.get_datastore_view()
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.Datastore,
            path_set=['name', 'summary.accessible'],
            include_mors=True
        )
        view.DestroyView()

        items = [
            pvc.widget.menu.MenuItem(
                tag=ds['name'],
                description='Accessible' if ds['summary.accessible'] else 'Not Accessible',
                on_select=pvc.widget.datastore.DatastoreWidget,
                on_select_args=(self.agent, self.dialog, ds['obj'])
            ) for ds in properties
        ]

        menu = pvc.widget.menu.Menu(
            title='Datastores',
            text='Select a Datastore from the menu',
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def virtual_machine_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...',
            width=40
        )

        view = self.agent.get_vm_view()
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.VirtualMachine,
            path_set=['name', 'runtime.powerState'],
            include_mors=True
        )
        view.DestroyView()

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm['name'],
                description=vm['runtime.powerState'],
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm['obj'])
            ) for vm in properties
        ]

        menu = pvc.widget.menu.Menu(
            title='Virtual Machines',
            text='Select a Virtual Machine from the menu that you wish to manage',
            items=items,
            dialog=self.dialog
        )

        menu.display()

    def network_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...',
            width=40
        )

        view = self.agent.get_container_view(
            obj_type=[pyVmomi.vim.Network]
        )

        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.Network,
            path_set=['name', 'summary.accessible'],
            include_mors=True
        )
        view.DestroyView()

        items = [
            pvc.widget.menu.MenuItem(
                tag=network['name'],
                description='Accessible' if network['summary.accessible'] else 'Not Accessible',
                on_select=pvc.widget.network.NetworkWidget,
                on_select_args=(self.agent, self.dialog, network['obj'])
            ) for network in properties
        ]

        menu = pvc.widget.menu.Menu(
            title='Networks',
            text='Select a network from the menu that you wish to manage',
            items=items,
            dialog=self.dialog
        )
        menu.display()
