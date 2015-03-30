"""
Docstring should go here

"""

import pyVmomi

import pvc.widget.form
import pvc.widget.menu

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
            text='Retrieving information ...'
        )

        items = [
            pvc.widget.menu.MenuItem(
                tag=alarm.entity.name,
                description=alarm.alarm.info.name,
                on_select=self.alarm_menu,
                on_select_args=(alarm,)
            ) for alarm in self.obj.triggeredAlarmState
        ]

        menu = pvc.widget.menu.Menu(
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
            pvc.widget.menu.MenuItem(
                tag='Details',
                description='View Alarm Details',
                on_select=self.details,
                on_select_args=(alarm,)
            ),
            pvc.widget.menu.MenuItem(
                tag='Acknowledge',
                description='Acknowledge Alarm',
                on_select=self.acknowledge,
                on_select_args=(alarm,)
            ),
            pvc.widget.menu.MenuItem(
                tag='Reset',
                description='Reset Alarm'
            ),
        ]

        menu = pvc.widget.menu.Menu(
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
            pvc.widget.form.FormElement(
                label='Entity',
                item=alarm.entity.name
            ),
            pvc.widget.form.FormElement(
                label='Status',
                item=alarm.overallStatus
            ),
            pvc.widget.form.FormElement(
                label='Name',
                item=alarm.alarm.info.name
            ),
            pvc.widget.form.FormElement(
                label='Triggered',
                item=str(alarm.time)
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged',
                item=str(alarm.acknowledged)
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged At',
                item=str(alarm.acknowledgedTime) if alarm.acknowledgedTime else ''
            ),
            pvc.widget.form.FormElement(
                label='Acknowledged By',
                item=alarm.acknowledgedByUser if alarm.acknowledgedByUser else ''
            )
        ]

        form = pvc.widget.form.Form(
            title=self.obj.name,
            dialog=self.dialog,
            form_elements=elements
        )

        return form.display()

    def acknowledge(self, alarm):
        """
        Acknowledge alarm

        Args:
            alarm (vim.AlarmState): A vim.AlarmState instance

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Acnowledging alarm ...'
        )

        am = self.agent.si.content.alarmManager
        am.AcknowledgeAlarm(
            alarm=alarm.alarm,
            entity=alarm.entity
        )
