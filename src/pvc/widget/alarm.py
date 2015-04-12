"""
Alarm Widgets

"""

import pvc.widget.form
import pvc.widget.menu

__all__ = ['AlarmWidget']


class AlarmWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Alarm Widget

        Args:
            agent      (VConnector): A VConnector instance
            dialog  (dialog.Dialog): A Dialog instance
            obj    (vim.AlarmState): A vim.AlarmState instance

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.title = '{} ({})'.format(self.obj.entity.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Details',
                description='View Alarm Details',
                on_select=self.details
            ),
            pvc.widget.menu.MenuItem(
                tag='Acknowledge',
                description='Acknowledge Alarm',
                on_select=self.acknowledge
            ),
            pvc.widget.menu.MenuItem(
                tag='Reset',
                description='Reset Alarm'
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()

    def details(self):
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Entity',
                item=self.obj.entity.name
            ),
            pvc.widget.form.FormElement(
                label='Status',
                item=self.obj.overallStatus
            ),
            pvc.widget.form.FormElement(
                label='Name',
                item=self.obj.alarm.info.name
            ),
            pvc.widget.form.FormElement(
                label='Triggered',
                item=str(self.obj.time)
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged',
                item=str(self.obj.acknowledged)
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged At',
                item=str(self.obj.acknowledgedTime) if self.obj.acknowledgedTime else ''
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged By',
                item=self.obj.acknowledgedByUser if self.obj.acknowledgedByUser else ''
            )
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Alarm details'
        )

        return form.display()

    def acknowledge(self, alarm):
        """
        Acknowledge alarm

        Args:
            alarm (vim.AlarmState): A vim.AlarmState instance

        """
        self.dialog.infobox(
            title=self.title,
            text='Acknowledging alarm ...'
        )

        am = self.agent.si.content.alarmManager
        am.AcknowledgeAlarm(
            alarm=alarm.alarm,
            entity=alarm.entity
        )
