"""
HostSystem Widgets

"""

import datetime

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.common
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.network
import pvc.widget.performance

__all__ = ['HostSystemWidget']


class HostSystemWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        HostSystem Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.HostSystem): A HostSystem managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='General',
                description='General information',
                on_select=self.info
            ),
            pvc.widget.menu.MenuItem(
                tag='Resources',
                description='Resource usage information',
                on_select=self.resources
            ),
            pvc.widget.menu.MenuItem(
                tag='Network',
                description='Host Networks',
                on_select=pvc.widget.common.network_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Performance',
                description='Performance Metrics',
                on_select=pvc.widget.performance.PerformanceProviderWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def info(self):
        """
        General information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='State',
                item=self.obj.runtime.connectionState
            ),
            pvc.widget.form.FormElement(
                label='Type',
                item=self.obj.config.product.fullName,
            ),
            pvc.widget.form.FormElement(
                label='Vendor',
                item=self.obj.hardware.systemInfo.vendor
            ),
            pvc.widget.form.FormElement(
                label='Model',
                item=self.obj.hardware.systemInfo.model
            ),
            pvc.widget.form.FormElement(
                label='Memory Size',
                item=humanize.naturalsize(self.obj.hardware.memorySize, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='CPU Packages',
                item=str(self.obj.hardware.cpuInfo.numCpuPackages)
            ),
            pvc.widget.form.FormElement(
                label='CPU Cores',
                item=str(self.obj.hardware.cpuInfo.numCpuCores)
            ),
            pvc.widget.form.FormElement(
                label='CPU Threads',
                item=str(self.obj.hardware.cpuInfo.numCpuThreads)
            ),
            pvc.widget.form.FormElement(
                label='Uptime',
                item=str(datetime.timedelta(seconds=self.obj.summary.quickStats.uptime))
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
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='CPU Usage',
                item='{} MHz'.format(self.obj.summary.quickStats.overallCpuUsage)
            ),
            pvc.widget.form.FormElement(
                label='Memory Usage',
                item='{} MB'.format(self.obj.summary.quickStats.overallMemoryUsage)
            ),
            pvc.widget.form.FormElement(
                label='CPU Fairness',
                item='{} MHz'.format(self.obj.summary.quickStats.distributedCpuFairness)
            ),
            pvc.widget.form.FormElement(
                label='Memory Fairness',
                item='{} MB'.format(self.obj.summary.quickStats.distributedMemoryFairness)
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
        )

        form.display()
