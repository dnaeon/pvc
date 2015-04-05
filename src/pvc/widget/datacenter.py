"""
Datacenter Widgets

"""

import pyVmomi

import pvc.widget.menu
import pvc.widget.performance

__all__ = ['DatacenterWidget']


class DatacenterWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Datacenter Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.Datacenter): A vim.Datacenter managed entity

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
                tag='Performance',
                description='Performance Metrics',
                on_select=pvc.widget.performance.PerformanceProviderWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select item from menu'
        )

        menu.display()

    def summary(self):
        """
        Datacenter general information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Overall Status',
                item=self.obj.overallStatus
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='Datacenter general information'
        )

        form.display()
