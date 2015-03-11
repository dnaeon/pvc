"""
Docstring should go here

"""

import pyVmomi

from pvc.widget.form import Form, FormElement
from pvc.widget.menu import Menu, MenuItem

__all__ = ['AlarmWidget']


class AlarmWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Inventory menu

        Args:
            agent         (VConnector): A VConnector instance
            dialog     (dialog.Dialog): A Dialog instance
            obj    (vim.ManagedEntity): A vim.ManagedEntity object

        """
        if not isinstance(obj, pyVmomi.vim.ManagedEntity):
            raise TypeError('Need a vim.ManagedEntity instance')

        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        if not self.obj.triggeredAlarmState:
            self.dialog.msgbox(
                title=self.obj.name,
                text='No triggered alarms'
            )
            return

        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving Alarms ...'
        )

        items = [
            MenuItem(
                tag=alarm.entity.name,
                description=alarm.alarm.info.name,
                on_select=self.alarm_menu,
                on_select_args=(alarm,)
            ) for alarm in self.obj.triggeredAlarmState
        ]

        menu = Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def alarm_menu(self, alarm):
        """
        Alarm menu

        Args:
            alarm (vim.AlarmState): A vim.AlarmState instance

        """
        items = [
            MenuItem(
                tag='Details',
                description='View Alarm Details',
                on_select=self.details,
                on_select_args=(alarm,)
            ),
            MenuItem(
                tag='Acknowledge',
                description='Acknowledge Alarm',
                on_select=self.acknowledge,
                on_select_args=(alarm,)
            ),
            MenuItem(
                tag='Clear',
                description='Clear Alarm',
                on_select=self.clear,
                on_select_args=(alarm,)
            ),
        ]

        menu = Menu(
            title=self.obj.name,
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def details(self, alarm):
        """
        View details about a triggered alarm

        Args:
            alarm (vim.AlarmState): A vim.AlarmState instance

        """
        elements = [
            FormElement(
                label='Entity',
                item=alarm.entity.name
            ),
            FormElement(
                label='Status',
                item=alarm.overallStatus
            ),
            FormElement(
                label='Name',
                item=alarm.alarm.info.name
            ),
            FormElement(
                label='Triggered',
                item=str(alarm.time)
            ),
            FormElement(
                label='Acknowledged',
                item=str(alarm.acknowledged)
            ),
            FormElement(
                label='Acknowledged At',
                item=str(alarm.acknowledgedTime) if alarm.acknowledgedTime else ''
            ),
            FormElement(
                label='Acknowledged By',
                item=alarm.acknowledgedByUser if alarm.acknowledgedByUser else ''
            )
        ]

        form = Form(
            title=self.obj.name,
            dialog=self.dialog,
            form_elements=elements
        )

        return form.display()

    def acknowledge(self, alarm):
        pass

    def clear(self, alarm):
        pass
