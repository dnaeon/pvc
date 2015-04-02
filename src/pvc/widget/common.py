"""
Common Widgets Module

"""

import pyVmomi

import pvc.widget.alarm
import pvc.widget.menu
import pvc.widget.gauge
import pvc.widget.datastore
import pvc.widget.network
import pvc.widget.hostsystem
import pvc.widget.session
import pvc.widget.virtualmachine

__all__ = [
    'rename', 'network_menu', 'datastore_menu',
    'host_menu', 'hostmount_menu', 'virtual_machine_menu',
    'session_menu', 'alarm_menu',
]


def rename(obj, dialog):
    """
    Rename a Managed Entity

    Args:
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dialog): A Dialog instance

    """
    code, new_name = dialog.inputbox(
        title=obj.name,
        text='New name for {}?'.format(obj.name),
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

def host_menu(agent, dialog, obj):
    """
    A widget to display a menu of HostSystem entities

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'host'):
        dialog.msgbox(
            title=obj.name,
            text='Entity does not contain a host property'
        )
        return

    view = agent.get_list_view(obj.host)
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.HostSystem,
        path_set=['name', 'runtime.connectionState'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title=obj.name,
            text='No hosts found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=host['name'],
            description=host['runtime.connectionState'],
            on_select=pvc.widget.hostsystem.HostSystemWidget,
            on_select_args=(agent, dialog, host['obj'])
        ) for host in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=''
    )

    menu.display()

def hostmount_menu(agent, dialog, obj):
    """
    A widget to display a menu of DatastoreHostMount instances

    To be used with datastores in order to provide a menu of
    hosts mounting a particular datastore

    Args:
        agent     (VConnector): A VConnector instance
        dialog (dialog.Dailog): A Dialog instance
        obj    (vim.Datastore): A Managed Entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'host'):
        dialog.msgbox(
            title=obj.name,
            text='Entity does not contain a host property'
        )
        return

    hosts = [h.key for h in obj.host]
    view = agent.get_list_view(hosts)
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.HostSystem,
        path_set=['name', 'runtime.connectionState'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title=obj.name,
            text='No hosts have mounted the datastore'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=host['name'],
            description=host['runtime.connectionState'],
            on_select=pvc.widget.hostsystem.HostSystemWidget,
            on_select_args=(agent, dialog, host['obj'])
        ) for host in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text='',
    )

    menu.display()

def network_menu(agent, dialog, obj):
    """
    A widget to display the networks by a Managed Entity

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'network'):
        dialog.msgbox(
            title=obj.name,
            text='Entity does not contain a network property'
        )
        return

    view = agent.get_list_view(obj.network)
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.Network,
        path_set=['name', 'summary.accessible'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title=obj.name,
            text='No networks found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=network['name'],
            description='Accessible' if network['summary.accessible'] else 'Not Accessible',
            on_select=pvc.widget.network.NetworkWidget,
            on_select_args=(agent, dialog, network['obj'])
        ) for network in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=''
    )

    menu.display()

def virtual_machine_menu(agent, dialog, obj):
    """
    A widget to display the VMs contained within a Managed Entity, e.g.
    HostSystem, ClusterComputeResource, Datastore, etc.

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

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
        text=''
    )

    menu.display()

def datastore_menu(agent, dialog, obj):
    """
    A widget to get all Datastores used by a managed entity, e.g.
    HostSystem, VirtualMachine, Cluster, etc.

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'datastore'):
        dialog.msgbox(
            title=obj.name,
            text='Entity does not contain a datastore property'
        )
        return

    view = agent.get_list_view(obj.datastore)
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.Datastore,
        path_set=['name', 'summary.accessible'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title=obj.name,
            text='No datastores found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=ds['name'],
            description='Accessible' if ds['summary.accessible'] else 'Not Accessible',
            on_select=pvc.widget.datastore.DatastoreWidget,
            on_select_args=(agent, dialog, ds['obj'])
        ) for ds in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text=''
    )

    menu.display()

def session_menu(agent, dialog):
    """
    A widget to display a menu of current sessions

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    try:
        sm = agent.si.content.sessionManager
        session_list = sm.sessionList
    except pyVmomi.vim.NoPermission:
        dialog.msgbox(
            title='Access Denied',
            text='No permissions to view sessions'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=session.key,
            description='{}@{}'.format(session.userName, session.ipAddress),
            on_select=pvc.widget.session.SessionWidget,
            on_select_args=(agent, dialog, session)
        ) for session in session_list
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title='Sessions',
        text='Select a session for more detais',
    )

    menu.display()

def alarm_menu(agent, dialog, obj):
    """
    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not obj.triggeredAlarmState:
        dialog.msgbox(
            title=obj.name,
            text='No triggered alarms'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=alarm.key,
            description=alarm.alarm.info.name,
            on_select=pvc.widget.alarm.AlarmWidget,
            on_select_args=(agent, dialog, alarm)
        ) for alarm in obj.triggeredAlarmState
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=obj.name,
        text='Select an alarm for more details'
    )

    menu.display()
