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
Inventory Widgets

"""

import pyVmomi

import pvc.widget.common
import pvc.widget.menu
import pvc.widget.datastore
import pvc.widget.hostsystem
import pvc.widget.network
import pvc.widget.radiolist
import pvc.widget.virtualmachine

__all__ = [
    'InventoryWidget', 'InventorySearchWidget',
    'InventorySearchHostWidget', 'InventorySearchVirtualMachineWidget',
    'InventoryDatacenterWidget',
]


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
                tag='Datacenters',
                description='Manage Datacenters',
                on_select=InventoryDatacenterWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Clusters',
                description='Manage Clusters',
                on_select=pvc.widget.common.cluster_menu,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Hosts',
                description='Manage hosts',
                on_select=self.host_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='VMs & Templates',
                description='Manage VMs & Templates',
                on_select=self.virtual_machine_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastores',
                description='Manage Datastores',
                on_select=self.datastore_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Networking',
                description='Manage Networking',
                on_select=self.network_menu
            ),
            pvc.widget.menu.MenuItem(
                tag='Search',
                description='Search Inventory',
                on_select=InventorySearchWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Menu',
            text='Select an item from the inventory'
        )

        menu.display()

    def host_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        view = self.agent.get_host_view()
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.HostSystem,
            path_set=['name', 'runtime.connectionState'],
            include_mors=True
        )
        view.DestroyView()

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
            title='Hosts',
            text='Select a host from the menu'
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
            items=items,
            dialog=self.dialog,
            title='Datastores',
            text='Select a Datastore from the menu'
        )

        menu.display()

    def virtual_machine_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...'
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
            items=items,
            dialog=self.dialog,
            title='Virtual Machines',
            text='Select a Virtual Machine from the menu'
        )

        menu.display()

    def network_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...'
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
            items=items,
            dialog=self.dialog,
            title='Networks',
            text='Select a network from the menu that you wish to manage'
        )

        menu.display()


class InventorySearchWidget(object):
    def __init__(self, agent, dialog):
        """
        Inventory search widget

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
                tag='Hosts',
                description='Search inventory for hosts',
                on_select=InventorySearchHostWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Virtual Machines',
                description='Search inventory for VMs',
                on_select=InventorySearchVirtualMachineWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search',
            text=''
        )

        menu.display()


class InventorySearchHostWidget(object):
    def __init__(self, agent, dialog):
        """
        Widget to search inventory for hosts

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
                tag='DNS',
                description='Find hosts by DNS name',
                on_select=self.find_by_dns
            ),
            pvc.widget.menu.MenuItem(
                tag='IP',
                description='Find hosts by IP address',
                on_select=self.find_by_ip
            ),
            pvc.widget.menu.MenuItem(
                tag='UUID',
                description='Find hosts by UUID',
                on_select=self.find_by_uuid
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search',
            text='Select criteria for searching of hosts'
        )

        menu.display()

    def find_by_dns(self):
        """
        Find hosts by their DNS name

        """
        result = pvc.widget.common.inventory_search_by_dns(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=False
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=host.name,
                description=host.runtime.connectionState,
                on_select=pvc.widget.hostsystem.HostSystemWidget,
                on_select_args=(self.agent, self.dialog, host)
            ) for host in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} hosts matching the search criteria'.format(len(result))
        )

        menu.display()

    def find_by_ip(self):
        """
        Find hosts by their IP address

        """
        result = pvc.widget.common.inventory_search_by_ip(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=False
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=host.name,
                description=host.runtime.connectionState,
                on_select=pvc.widget.hostsystem.HostSystemWidget,
                on_select_args=(self.agent, self.dialog, host)
            ) for host in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} hosts matching the search criteria'.format(len(result))
        )

        menu.display()

    def find_by_uuid(self):
        """
        Find hosts by their UUID

        """
        result = pvc.widget.common.inventory_search_by_uuid(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=False
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=host.name,
                description=host.runtime.connectionState,
                on_select=pvc.widget.hostsystem.HostSystemWidget,
                on_select_args=(self.agent, self.dialog, host)
            ) for host in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} hosts matching the search criteria'.format(len(result))
        )

        menu.display()


class InventorySearchVirtualMachineWidget(object):
    def __init__(self, agent, dialog):
        """
        Widget to search inventory for virtual machines

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
                tag='DNS',
                description='Find VMs by DNS name',
                on_select=self.find_by_dns
            ),
            pvc.widget.menu.MenuItem(
                tag='IP',
                description='Find VMs by IP address',
                on_select=self.find_by_ip
            ),
            pvc.widget.menu.MenuItem(
                tag='UUID',
                description='Find VMs by UUID',
                on_select=self.find_by_uuid
            ),
            pvc.widget.menu.MenuItem(
                tag='Datastore Path',
                description='Find VM by its location on a datastore',
                on_select=self.find_by_datastore_path
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search',
            text='Select criteria for searching of hosts'
        )

        menu.display()

    def find_by_dns(self):
        """
        Find virtual machines by their DNS name

        """
        result = pvc.widget.common.inventory_search_by_dns(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=True
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm.name,
                description=vm.runtime.powerState,
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm)
            ) for vm in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} virtual machines matching the search criteria'.format(len(result))
        )

        menu.display()

    def find_by_ip(self):
        """
        Find virtual machines by their IP address

        """
        result = pvc.widget.common.inventory_search_by_ip(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=True
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm.name,
                description=vm.runtime.powerState,
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm)
            ) for vm in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} virtual machines matching the search criteria'.format(len(result))
        )

        menu.display()

    def find_by_uuid(self):
        """
        Find virtual machines by their UUID

        """
        result = pvc.widget.common.inventory_search_by_uuid(
            agent=self.agent,
            dialog=self.dialog,
            vm_search=True
        )

        if not result:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm.name,
                description=vm.runtime.powerState,
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm)
            ) for vm in result
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text='Found {} virtual machines matching the search criteria'.format(len(result))
        )

        menu.display()

    def find_by_datastore_path(self):
        """
        Find virtual machine it's localtion on a datastore

        """
        datacenter = pvc.widget.common.choose_datacenter(
            agent=self.agent,
            dialog=self.dialog,
            all_datacenters_option=False
        )

        if not datacenter:
            self.dialog.msgbox(
                title='Error',
                text='No datacenter specified for inventory search'
            )
            return

        code, path = self.dialog.inputbox(
            title='Inventory Search',
            text='Specify datastore path to the .vmx file'
        )

        if not path:
            self.dialog.msgbox(
                title='Error',
                text='Invalid input provided'
            )
            return

        self.dialog.infobox(
            text='Searching Inventory ...'
        )

        vm = self.agent.si.content.searchIndex.FindByDatastorePath(
            datacenter=datacenter,
            path=path
        )

        if not vm:
            self.dialog.msgbox(
                title='Inventory Search',
                text='No results found'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=vm.name,
                description=vm.runtime.powerState,
                on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
                on_select_args=(self.agent, self.dialog, vm)
            )
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Search Results',
            text=''
        )

        menu.display()


class InventoryDatacenterWidget(object):
    def __init__(self, agent, dialog):
        """
        Inventory Datacenter Widget

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
                tag='Create',
                description='Create new datacenter',
                on_select=self.create_datacenter
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View datacenters',
                on_select=pvc.widget.common.datacenter_menu,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Inventory Datacenter Menu',
            text='Select an item from the inventory'
        )

        menu.display()

    def create_datacenter(self):
        """
        Create a new Datacenter

        """
        folder = pvc.widget.common.choose_folder(
            agent=self.agent,
            dialog=self.dialog
        )

        code, name = self.dialog.inputbox(
            title='Create Datacenter',
            text='Provide name for the Datacenter'
        )

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not name:
            self.dialog.msgbox(
                title='Error',
                text='Invalid input provided'
            )
            return

        self.dialog.infobox(
            text='Creating datacenter {} ...'.format(name)
        )

        try:
            folder.CreateDatacenter(name=name)
        except pyVmomi.vim.MethodFault as e:
            self.dialog.msgbox(
                title='Error',
                text=e.msg
            )
