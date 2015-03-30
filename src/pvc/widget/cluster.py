"""
Cluster Widgets

"""

import humanize

import pvc.widget.menu
import pvc.widget.form

__all__ = ['ClusterWidget']


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
