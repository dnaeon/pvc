"""
Docstring should go here

"""

import pyVmomi

import pvc.widget.cluster
import pvc.widget.menu
import pvc.widget.datastore
import pvc.widget.hostsystem
import pvc.widget.network
import pvc.widget.radiolist
import pvc.widget.virtualmachine

__all__ = [
    'choose_datacenter', 'inventory_search_by_dns',
    'inventory_search_by_ip', 'inventory_search_by_uuid',
    'InventoryWidget', 'InventorySearchWidget',
    'InventorySearchHostWidget', 'InventorySearchVirtualMachineWidget',
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
                tag='Clusters',
                description='Manage Clusters',
                on_select=self.cluster_menu
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

    def cluster_menu(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        view = self.agent.get_cluster_view()
        properties = self.agent.collect_properties(
            view_ref=view,
            obj_type=pyVmomi.vim.ClusterComputeResource,
            path_set=['name', 'overallStatus'],
            include_mors=True
        )
        view.DestroyView()

        items = [
            pvc.widget.menu.MenuItem(
                tag=cluster['name'],
                description=cluster['overallStatus'],
                on_select=pvc.widget.cluster.ClusterWidget,
                on_select_args=(self.agent, self.dialog, cluster['obj'])
            ) for cluster in properties
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Clusters',
            text='\nSelect a cluster from the menu\n'
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
        items=[
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
        result = inventory_search_by_dns(
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
        result = inventory_search_by_ip(
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
        result = inventory_search_by_uuid(
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
        items=[
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
        result = inventory_search_by_dns(
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
        result = inventory_search_by_ip(
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
        result = inventory_search_by_uuid(
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
                description=host.runtime.powerState,
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
        datacenter = choose_datacenter(
            agent=agent,
            dialog=dialog,
            all_datacenters_option=True
        )

        code, path = dialog.inputbox(
            title='Inventory Search',
            text='Specify datastore path to the .vmx file'
        )

        if not path:
            dialog.msgbox(
                title='Error',
                text='Invalid input provided'
            )
            return

        dialog.infobox(
            text='Searching Inventory ...'
        )

        if datacenter:
            vm = agent.si.content.searchIndex.FindByDatastorePath(
                datacenter=datacenter,
                path=path
            )
        else:
            vm = agent.si.content.searchIndex.FindByDatastorePath(
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

def choose_datacenter(agent, dialog, all_datacenters_option):
    """
    Prompts the user to choose a datacenter

    Convinience function that can be used to choose a datacenter,
    which result can be used for example to restrict search of
    inventory to a specific datacenter only, or be used for other
    purposes, e.g. choosing a datacenter where to deploy a Virtual Machine.

    Args:
        agent            (VConnector): A VConnector instance
        dialog        (dialog.Dialog): A Dialog instance
        all_datacenters_option (bool): If True then an option to choose all
                                       datacenter is provided as well

    Returns:
        A vim.Datacenter managed entity if a datacenter has been
        selected. Returns None if there are no datacenters found or
        if selected the 'All Datacenters' option.

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    view = agent.get_datacenter_view()
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.Datacenter,
        path_set=['name'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        return

    items = []
    if all_datacenters_option:
        items.append(
            pvc.widget.radiolist.RadioListItem(tag='All Datacenters')
        )

    datacenters = [
        pvc.widget.radiolist.RadioListItem(tag=datacenter['name'])
        for datacenter in properties
    ]
    items.extend(datacenters)

    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Datacenter',
        text='Choose a Datacenter from the list below'
    )

    code, tag = radiolist.display()

    if not tag:
        return
    elif all_datacenters_option and tag == 'All Datacenters':
        return

    return [d['obj'] for d in properties if d['name'] == tag].pop()

def inventory_search_by_dns(agent, dialog, vm_search):
    """
    Search inventory for managed objects by their DNS name

    Args:
        agent (VConnector): A VConnector instance
        dialog    (Dialog): A Dialog instance
        vm_search   (bool): If True search for VMs only, otherwise
                            search for hosts only

    """
    datacenter = choose_datacenter(
        agent=agent,
        dialog=dialog,
        all_datacenters_option=True
    )

    code, name = dialog.inputbox(
            title='Inventory Search',
            text='Specify DNS name to search for'
        )

    if not name:
        dialog.msgbox(
            title='Error',
            text='Invalid input provided'
        )
        return

    dialog.infobox(
        text='Searching Inventory ...'
    )

    if datacenter:
        result = agent.si.content.searchIndex.FindAllByDnsName(
            datacenter=datacenter,
            dnsName=name,
            vmSearch=vm_search
        )
    else:
        result = agent.si.content.searchIndex.FindAllByDnsName(
            dnsName=name,
            vmSearch=vm_search
        )

    return result

def inventory_search_by_ip(agent, dialog, vm_search):
    """
    Search inventory for managed objects by their IP address

    Args:
        agent (VConnector): A VConnector instance
        dialog    (Dialog): A Dialog instance
        vm_search   (bool): If True search for VMs only, otherwise
                            search for hosts only

    """
    datacenter = choose_datacenter(
        agent=agent,
        dialog=dialog,
        all_datacenters_option=True
    )

    code, ipaddr = dialog.inputbox(
            title='Inventory Search',
            text='Specify IP address to search for'
        )

    if not ipaddr:
        dialog.msgbox(
            title='Error',
            text='Invalid input provided'
        )
        return

    dialog.infobox(
        text='Searching Inventory ...'
    )

    if datacenter:
        result = agent.si.content.searchIndex.FindAllByIp(
            datacenter=datacenter,
            ip=ipaddr,
            vmSearch=vm_search
        )
    else:
        result = agent.si.content.searchIndex.FindAllByIp(
            ip=ipaddr,
            vmSearch=vm_search
        )

    return result

def inventory_search_by_uuid(agent, dialog, vm_search):
    """
    Search inventory for managed objects by their UUID

    Args:
        agent (VConnector): A VConnector instance
        dialog    (Dialog): A Dialog instance
        vm_search   (bool): If True search for VMs only, otherwise
                            search for hosts only

    """
    datacenter = choose_datacenter(
        agent=agent,
        dialog=dialog,
        all_datacenters_option=True
    )

    code, uuid = dialog.inputbox(
            title='Inventory Search',
            text='Specify UUID to search for'
        )

    if not uuid:
        dialog.msgbox(
            title='Error',
            text='Invalid input provided'
        )
        return

    dialog.infobox(
        text='Searching Inventory ...'
    )

    if datacenter:
        result = agent.si.content.searchIndex.FindAllByUuid(
            datacenter=datacenter,
            uuid=uuid,
            vmSearch=vm_search
        )
    else:
        result = agent.si.content.searchIndex.FindAllByUuid(
            uuid=uuid,
            vmSearch=vm_search
        )

    return result

