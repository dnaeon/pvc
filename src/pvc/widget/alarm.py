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
Alarm Widgets

"""

import pvc.widget.debug
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
            pvc.widget.menu.MenuItem(
                tag='Debug',
                description='Start a Python REPL console',
                on_select=pvc.widget.debug.DebugWidget,
                on_select_args=(locals(), globals())
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
