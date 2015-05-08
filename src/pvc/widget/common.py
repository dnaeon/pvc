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
Common Widgets Module

"""

import pyVmomi

import pvc.widget.alarm
import pvc.widget.cluster
import pvc.widget.datacenter
import pvc.widget.menu
import pvc.widget.gauge
import pvc.widget.datastore
import pvc.widget.network
import pvc.widget.hostsystem
import pvc.widget.session
import pvc.widget.radiolist
import pvc.widget.virtualmachine

__all__ = [
    'rename', 'network_menu', 'datastore_menu',
    'host_menu', 'hostmount_menu', 'virtual_machine_menu',
    'session_menu', 'alarm_menu', 'choose_folder',
    'choose_datacenter', 'choose_cluster', 'choose_datastore',
    'inventory_search_by_dns', 'inventory_search_by_ip',
    'inventory_search_by_uuid', 'datacenter_menu', 'remove',
    'choose_network', 'host_service_menu',
]


def rename(obj, dialog):
    """
    Rename a Managed Entity

    Args:
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dialog): A Dialog instance

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    code, new_name = dialog.inputbox(
        title=title,
        text='New name for {}?'.format(obj.name),
        init=obj.name
    )

    if code in (dialog.CANCEL, dialog.ESC):
        return

    task = obj.Rename(newName=new_name)
    gauge = pvc.widget.gauge.TaskGauge(
        dialog=dialog,
        task=task,
        title=title,
        text='Renaming {} to {} ...'.format(obj.name, new_name)
    )

    gauge.display()


def remove(obj, dialog):
    """
    Remove a Managed Entity

    NOTE: This operation also removes any child objects of the
          managed entity.

    Args:
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dialog): A Dialog instance

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    code = dialog.yesno(
        title=title,
        text='Remove {} and all child objects?'.format(obj.name)
    )

    if code in (dialog.CANCEL, dialog.ESC):
        return

    task = obj.Destroy()
    gauge = pvc.widget.gauge.TaskGauge(
        dialog=dialog,
        task=task,
        title=title,
        text='Removing {} and any child objects ...'.format(obj.name)
    )

    gauge.display()


def datacenter_menu(agent, dialog, folder=None):
    """
    A widget to display a menu of Datacenter entities

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        folder        (vim.Folder): A vim.Folder entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not folder:
        folder = agent.si.content.rootFolder

    view = agent.get_container_view(
        obj_type=[pyVmomi.vim.Datacenter],
        container=folder
    )
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.Datacenter,
        path_set=['name', 'overallStatus'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title='No objects found',
            text='No datacenters managed entities found'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=dc['name'],
            description=dc['overallStatus'],
            on_select=pvc.widget.datacenter.DatacenterWidget,
            on_select_args=(agent, dialog, dc['obj'])
        ) for dc in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title='Select Datacenter',
        text=''
    )

    menu.display()


def cluster_menu(agent, dialog, folder=None):
    """
    A widget to display a menu of vim.ClusterComputeResource entities

    Args:
        agent     (VConnector): A VConnector instance
        dialog (dialog.Dailog): A Dialog instance
        folder    (vim.Folder): A vim.Folder entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not folder:
        folder = agent.si.content.rootFolder

    view = agent.get_container_view(
        obj_type=[pyVmomi.vim.ClusterComputeResource],
        container=folder
    )
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.ClusterComputeResource,
        path_set=['name', 'overallStatus'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title='No objects found',
            text='No cluster managed entities found'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=cluster['name'],
            description=cluster['overallStatus'],
            on_select=pvc.widget.cluster.ClusterWidget,
            on_select_args=(agent, dialog, cluster['obj'])
        ) for cluster in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title='Select Cluster',
        text=''
    )

    menu.display()


def host_menu(agent, dialog, obj):
    """
    A widget to display a menu of HostSystem entities

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'host'):
        dialog.msgbox(
            title=title,
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
            title=title,
            text='No hosts found on this managed entity'
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
        title=title,
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
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'host'):
        dialog.msgbox(
            title=title,
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
            title=title,
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
        title=title,
        text='',
    )

    menu.display()


def host_service_menu(agent, dialog, obj):
    """
    A widget to display a menu of services in a HostSystem

    Args:
        agent      (VConnector): A VConnector instance
        dialog  (dialog.Dailog): A Dialog instance
        obj    (vim.HostSystem): A HostSystem entity

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    items = [
        pvc.widget.menu.MenuItem(
            tag=service.key,
            description=service.label,
            on_select=pvc.widget.hostsystem.HostSystemServiceWidget,
            on_select_args=(agent, dialog, obj, service)
        ) for service in obj.config.service.service
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=title,
        text='Choose a service to manage'
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
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'network'):
        dialog.msgbox(
            title=title,
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
            title=title,
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
        title=title,
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
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'vm'):
        dialog.msgbox(
            title=title,
            text='Entity does not contain a vm property'
        )
        return

    view = agent.get_list_view(obj.vm)
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.VirtualMachine,
        path_set=['name', 'runtime.powerState'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        dialog.msgbox(
            title=title,
            text='No virtual machines found for this managed entity'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=vm['name'],
            description=vm['runtime.powerState'],
            on_select=pvc.widget.virtualmachine.VirtualMachineWidget,
            on_select_args=(agent, dialog, vm['obj'])
        ) for vm in properties
    ]

    menu = pvc.widget.menu.Menu(
        items=items,
        dialog=dialog,
        title=title,
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
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'datastore'):
        dialog.msgbox(
            title=title,
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
            title=title,
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
        title=title,
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
        title='Sessions',
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
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not obj.triggeredAlarmState:
        dialog.msgbox(
            title=title,
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
        title=title,
        text='Select an alarm for more details'
    )

    menu.display()


def choose_folder(agent, dialog):
    """
    Prompts the user to choose a folder

    Args:
        agent            (VConnector): A VConnector instance
        dialog        (dialog.Dialog): A Dialog instance

    Returns:
        A vim.Folder managed entity

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    view = agent.get_container_view(obj_type=[pyVmomi.vim.Folder])
    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.Folder,
        path_set=['name'],
        include_mors=True
    )
    view.DestroyView()

    # Remove all occurrencies of 'vm', 'host', 'datastore' and
    # 'network' from the collected folders as these ones are
    # reserved and we cannot create a datacenter there
    folders = [f for f in properties if f['name'] not in ('vm', 'host', 'datastore', 'network')]

    if not folders:
        return agent.si.content.rootFolder

    items = [
        pvc.widget.radiolist.RadioListItem(tag=folder['name'])
        for folder in folders
    ]
    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Folder',
        text='Choose a folder or CANCEL to select the root folder',
    )

    code, tag = radiolist.display()

    if not tag:
        return agent.si.content.rootFolder

    return [f['obj'] for f in properties if f['name'] == tag].pop()


def choose_datacenter(agent, dialog, all_datacenters_option=False):
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


def choose_cluster(agent, dialog, folder=None):
    """
    Prompts the user to choose a cluster

    Args:
        agent     (VConnector): A VConnector instance
        dialog (dialog.Dailog): A Dialog instance
        folder    (vim.Folder): A vim.Folder entity

    Returns:
        A vim.ClusterComputeResource managed entity if the
        user chose a cluster.

        Returns None if no cluster has been
        selected or there are no clusters existing

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not folder:
        folder = agent.si.content.rootFolder

    view = agent.get_container_view(
        obj_type=[pyVmomi.vim.ClusterComputeResource],
        container=folder
    )

    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.ClusterComputeResource,
        path_set=['name', 'overallStatus'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        return

    items = [
        pvc.widget.radiolist.RadioListItem(
            tag=cluster['name'],
            description=cluster['overallStatus'],
        ) for cluster in properties
    ]

    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Cluster',
        text='Choose a cluster from the list below'
    )

    code, tag = radiolist.display()

    if code in (dialog.CANCEL, dialog.ESC) or not tag:
        return

    return [c['obj'] for c in properties if c['name'] == tag].pop()


def choose_host(agent, dialog, folder=None):
    """
    Prompts the user to choose a host

    Args:
        agent     (VConnector): A VConnector instance
        dialog (dialog.Dailog): A Dialog instance
        folder    (vim.Folder): A vim.Folder entity

    Returns:
        A vim.HostSystem managed entity if the
        user chose a host.

        Returns None if no host has been
        selected or there are no hosts existing

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not folder:
        folder = agent.si.content.rootFolder

    view = agent.get_container_view(
        obj_type=[pyVmomi.vim.HostSystem],
        container=folder
    )

    properties = agent.collect_properties(
        view_ref=view,
        obj_type=pyVmomi.vim.HostSystem,
        path_set=['name', 'runtime.connectionState'],
        include_mors=True
    )
    view.DestroyView()

    if not properties:
        return

    items = [
        pvc.widget.radiolist.RadioListItem(
            tag=host['name'],
            description=host['runtime.connectionState'],
        ) for host in properties
    ]

    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Host',
        text='Choose a host from the list below'
    )

    code, tag = radiolist.display()

    if code in (dialog.CANCEL, dialog.ESC) or not tag:
        return

    return [h['obj'] for h in properties if h['name'] == tag].pop()


def choose_datastore(agent, dialog, obj):
    """
    Prompts the user to choose a datastore

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    Returns:
        A vim.Datastore managed entity if a datastore has been
        chosen

        Return None if no datastore has been selected or
        there are no datastores existing

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'datastore'):
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
        return

    items = [
        pvc.widget.radiolist.RadioListItem(
            tag=ds['name'],
            description='Accessible' if ds['summary.accessible'] else 'Not Accessible',
        ) for ds in properties
    ]

    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Datastore',
        text='Choose a datastore from the list below'
    )

    code, tag = radiolist.display()

    if code in (dialog.CANCEL, dialog.ESC) or not tag:
        return

    return [ds['obj'] for ds in properties if ds['name'] == tag].pop()


def choose_network(agent, dialog, obj):
    """
    Prompts the user to choose a network

    Args:
        agent         (VConnector): A VConnector instance
        dialog     (dialog.Dailog): A Dialog instance
        obj    (vim.ManagedEntity): A Managed Entity

    Returns:
        A vim.Network managed entity if a network has been
        chosen

        Return None if no network has been selected or
        there are no networks existing

    """
    title = '{} ({})'.format(obj.name, obj.__class__.__name__)

    dialog.infobox(
        title=title,
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'network'):
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
        return

    items = [
        pvc.widget.radiolist.RadioListItem(
            tag=network['name'],
            description='Accessible' if network['summary.accessible'] else 'Not Accessible',
        ) for network in properties
    ]

    radiolist = pvc.widget.radiolist.RadioList(
        items=items,
        dialog=dialog,
        title='Choose Network',
        text='Choose a network from the list below'
    )

    code, tag = radiolist.display()

    if code in (dialog.CANCEL, dialog.ESC) or not tag:
        return

    return [network['obj'] for network in properties if network['name'] == tag].pop()


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
