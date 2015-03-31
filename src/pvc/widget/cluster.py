"""
Cluster Widgets

"""

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.menu
import pvc.widget.performance

__all__ = ['ClusterWidget', 'ClusterActionWidget', 'ClusterHostWidget']


class ClusterWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Summary',
                description='General information',
                on_select=self.summary
            ),
            pvc.widget.menu.MenuItem(
                tag='Resources',
                description='Resource usage information',
                on_select=self.resources
            ),
            pvc.widget.menu.MenuItem(
                tag='Actions',
                description='Available Actions',
                on_select=ClusterActionWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Hosts',
                description='Manage hosts in cluster',
                on_select=ClusterHostWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Networks',
                description='Networking',
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
                tag='Alarms',
                description='View triggered alarms',
                on_select=pvc.widget.alarm.AlarmWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )

        menu.display()

    def summary(self):
        """
        Cluster general information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Hosts',
                item=str(self.obj.summary.numHosts)
            ),
            pvc.widget.form.FormElement(
                label='vMotion Migrations',
                item=str(self.obj.summary.numVmotions)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Cores',
                item=str(self.obj.summary.numCpuCores)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Threads',
                item=str(self.obj.summary.numCpuThreads)
            ),
            pvc.widget.form.FormElement(
                label='Total CPU Resources',
                item='{} MHz'.format(self.obj.summary.totalCpu)
            ),
            pvc.widget.form.FormElement(
                label='Total Memory',
                item=humanize.naturalsize(self.obj.summary.totalMemory, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Overall Status',
                item=self.obj.overallStatus
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name
        )

        form.display()

    def resources(self):
        """
        Resource usage information

        """
        text = (
            'Not implemented yet.\n'
            'See https://github.com/vmware/pyvmomi/issues/229 '
            'for more information.\n'
        )

        self.dialog.msgbox(
            title=self.obj.name,
            text=text
        )


class ClusterActionWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Actions Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Rename',
                description='Rename cluster',
                on_select=pvc.widget.common.rename,
                on_select_args=(self.obj, self.dialog, 'New cluster name?')
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            dialog=self.dialog,
            items=items
        )

        menu.display()


class ClusterHostWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Cluster Host Widget

        Args:
            agent                  (VConnector): A VConnector instance
            dialog              (dialog.Dialog): A Dialog instance
            obj    (vim.ClusterComputeResource): A ClusterComputeResource managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Connect',
                description='Connect host to cluster',
                on_select=self.connect_host
            ),
            pvc.widget.menu.MenuItem(
                tag='Disconnect',
                description='Disconnect host from cluster'
            ),
            pvc.widget.menu.MenuItem(
                tag='View',
                description='View hosts in cluster',
                on_select=pvc.widget.common.host_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )

        menu.display()

    def connect_host(self):
        """
        Connect a host to the cluster and add it to the inventory

        """
        text = (
            '\nEnter hostname or IP address of the '
            'host to be connected to cluster {}\n'
        )

        elements = [
            pvc.widget.form.FormElement(label='Hostname'),
            pvc.widget.form.FormElement(label='SSL Thumbprint'),
            pvc.widget.form.FormElement(label='Username'),
            pvc.widget.form.FormElement(label='Password', attributes=0x1),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title='Connect host to cluster',
            text=text.format(self.obj.name),
            mixed_form=True
        )

        code, fields = form.display()

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        if not all(fields.values()):
            self.dialog.msgbox(
                title='Error',
                text='Invalid input provided'
            )
            return

        connect_spec = pyVmomi.vim.HostConnectSpec(
            hostName=fields['Hostname'],
            sslThumbprint=fields['SSL Thumbprint'],
            userName=fields['Username'],
            password=fields['Password']
        )

        task = self.obj.AddHost(
            spec=connect_spec,
            asConnected=True
        )

        gauge = pvc.widget.gauge.TaskGauge(
            title=self.obj.name,
            text='\nConnecting {} to cluster ...'.format(fields['Hostname']),
            dialog=self.dialog,
            task=task
        )

        gauge.display()
