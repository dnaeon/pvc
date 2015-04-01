"""
Common Widgets Module

"""

import pvc.widget.menu
import pvc.widget.gauge
import pvc.widget.datastore
import pvc.widget.network
import pvc.widget.hostsystem
import pvc.widget.virtualmachine

__all__ = [
    'rename', 'network_menu', 'datastore_menu', 'virtual_machine_menu',
]


def rename(obj, dialog, text=''):
    """
    Rename a Managed Entity

    Args:
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dialog): A Dialog instance
        text                 (str): Text to display

    """
    code, new_name = dialog.inputbox(
        title=obj.name,
        text=text,
        init=obj.name
    )

    if code in (dialog.CANCEL, dialog.ESC):
        return

    task = obj.Rename(newName=new_name)
    gauge = pvc.widget.gauge.TaskGauge(
        dialog=dialog,
        task=task,
        title=obj.name,
        text='Renaming {} to {} ...'.format(obj.name, new_name)
    )

    gauge.display()

def host_menu(agent, dialog, obj, text=''):
    """
    A widget to display a menu of HostSystem entities

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity
        text                 (str): Text to display

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not obj.host:
        dialog.msgbox(
            title=obj.name,
            text='No hosts found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=host.name,
            description=host.runtime.connectionState,
            on_select=pvc.widget.hostsystem.HostSystemWidget,
            on_select_args=(agent, dialog, host)
        ) for host in obj.host
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=text
    )

    menu.display()

def hostmount_menu(agent, dialog, obj, text=''):
    """
    A widget to display a menu of DatastoreHostMount instances

    To be used with datastores in order to provide a menu of
    hosts mounting a particular datastore

    Args:
        agent     (VConnector): A VConnector instance
        dialog (dialog.Dailog): A Dialog instance
        obj    (vim.Datastore): A Managed Entity
        text             (str): Text to display

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not obj.host:
        dialog.msgbox(
            title=obj.name,
            text='No hosts have mounted the datastore'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=hostmount.key.name,
            description=hostmount.key.runtime.connectionState,
            on_select=pvc.widget.hostsystem.HostSystemWidget,
            on_select_args=(agent, dialog, hostmount.key)
        ) for hostmount in obj.host
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=text,
    )

    menu.display()

def network_menu(agent, dialog, obj, text=''):
    """
    A widget to display the networks by a Managed Entity

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity
        text                 (str): Text to display

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not obj.network:
        dialog.msgbox(
            title=obj.name,
            text='No networks found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=network.name,
            description='Accessible' if network.summary.accessible else 'Not Accessible',
            on_select=pvc.widget.network.NetworkWidget,
            on_select_args=(agent, dialog, network)
        ) for network in obj.network
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=text
    )

    menu.display()

def virtual_machine_menu(agent, dialog, obj, text=''):
    """
    A widget to display the VMs contained within a Managed Entity, e.g.
    HostSystem, ClusterComputeResource, Datastore, etc.

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity
        text                 (str): Text to display

    """
    dialog.infobox(
        title=obj.name,
        text='Retrieving information ...'
    )

    if not obj.vm:
        dialog.msgbox(
            title=obj.name,
            text='No virtual machines found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=vm.name,
            description=vm.runtime.powerState,
            on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
            on_select_args=(agent, dialog, vm)
        ) for vm in obj.vm
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=text
    )

    menu.display()

def datastore_menu(agent, dialog, obj, text=''):
    """
    A widget to get all Datastores used by a managed entity, e.g.
    HostSystem, VirtualMachine, Cluster, etc.

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity
        text                 (str): Text to display

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not obj.datastore:
        dialog.msgbox(
            title=obj.name,
            text='No datastores found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=ds.name,
            description='Accessible' if ds.summary.accessible else 'Not Accessible',
            on_select=pvc.widget.datastore.DatastoreWidget,
            on_select_args=(agent, dialog, ds)
        ) for ds in obj.datastore
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=text
    )

    menu.display()
