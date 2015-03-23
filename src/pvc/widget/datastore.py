"""
Datastore Widgets

"""

import pyVmomi
import humanize

import pvc.widget.alarm
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.gauge
import pvc.widget.performance

__all__ = ['DatastoreWidget']


class DatastoreWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Datastore Widget

        Args:
            agent     (VConnector): A VConnector instance
            dialog (dialog.Dialog): A Dialog instance
            obj    (vim.Datastore): A Datastore managed entity

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
                tag='Capacity',
                description='Datastore Capacity ',
                on_select=self.capacity
            ),
            pvc.widget.menu.MenuItem(
                tag='Performance',
                description='Performance Metrics',
                on_select=pvc.widget.performance.PerformanceProviderWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Tasks & Events',
                description='View Tasks & Events'
            ),
            pvc.widget.menu.MenuItem(
                tag='Alarms',
                description='View triggered alarms',
                on_select=pvc.widget.alarm.AlarmWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Rename',
                description='Rename Datastore',
                on_select=self.rename
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
        Datastore general information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Name',
                item=self.obj.name,
            ),
            pvc.widget.form.FormElement(
                label='Location',
                item=self.obj.summary.url
            ),
            pvc.widget.form.FormElement(
                label='Type',
                item=self.obj.summary.type
            ),
            pvc.widget.form.FormElement(
                label='Accessible',
                item=str(self.obj.summary.accessible)
            ),
            pvc.widget.form.FormElement(
                label='Maintenance Mode',
                item=self.obj.summary.maintenanceMode
            ),
            pvc.widget.form.FormElement(
                label='Multiple Host Access',
                item=str(self.obj.summary.multipleHostAccess)
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\Datastore General Information\n'
        )

        form.display()

    def capacity(self):
        """
        Datastore Capacity Information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Capacity',
                item=humanize.naturalsize(self.obj.summary.capacity, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Free Space',
                item=humanize.naturalsize(self.obj.summary.freeSpace, binary=True)
            ),
            pvc.widget.form.FormElement(
                label='Uncommitted Space',
                item=humanize.naturalsize(self.obj.summary.uncommitted, binary=True)
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='\nDatastore Capacity Information\n'
        )

        return form.display()

    def rename(self):
        """
        Rename Datastore

        """
        code, new_name = self.dialog.inputbox(
            title=self.obj.name,
            text='New datastore name?',
            init=self.obj.name
        )

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        task = self.obj.Rename(newName=new_name)
        gauge = pvc.widget.gauge.TaskGauge(
            title=self.obj.name,
            text='Renaming {} to {} ...'.format(self.obj.name, new_name),
            dialog=self.dialog,
            task=task
        )

        gauge.display()
