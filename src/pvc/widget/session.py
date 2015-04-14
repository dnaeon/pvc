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
Session module

"""

import pvc.widget.debug
import pvc.widget.menu
import pvc.widget.form

__all__ = ['SessionWidget']


class SessionWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Session Widget

        Args:
            agent        (VConnector): A VConnector instance
            dialog    (dialog.Dialog): A Dialog instance
            session (vim.UserSession): A vim.UserSession instance

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Details',
                description='View Session Details',
                on_select=self.details
            ),
            pvc.widget.menu.MenuItem(
                tag='Terminate',
                description='Terminate Session',
                on_select=self.terminate
            ),
            pvc.widget.menu.MenuItem(
                tag='Debug',
                description='Start a Python REPL console',
                on_select=pvc.widget.debug.DebugWidget,
                on_select_args=(locals(), globals())
            ),
        ]

        current_session = self.agent.si.content.sessionManager.currentSession
        if current_session.key == self.obj.key:
            title = 'Session {}@{} (This Session)'
        else:
            title = 'Session {}@{}'

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=title.format(self.obj.userName, self.obj.ipAddress),
            text='Select an action to be performed'
        )

        menu.display()

    def details(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Username',
                item=self.obj.userName
            ),
            pvc.widget.form.FormElement(
                label='Full Name',
                item=self.obj.fullName
            ),
            pvc.widget.form.FormElement(
                label='Login Time',
                item=str(self.obj.loginTime)
            ),
            pvc.widget.form.FormElement(
                label='Last Active',
                item=str(self.obj.lastActiveTime)
            ),
            pvc.widget.form.FormElement(
                label='Idle',
                item=str(self.agent.si.CurrentTime() - self.obj.lastActiveTime)
            ),
            pvc.widget.form.FormElement(
                label='IP Address',
                item=self.obj.ipAddress
            ),
            pvc.widget.form.FormElement(
                label='User Agent',
                item=self.obj.userAgent
            ),
            pvc.widget.form.FormElement(
                label='API Invocations',
                item=str(self.obj.callCount)
            ),
        ]

        current_session = self.agent.si.content.sessionManager.currentSession
        if current_session.key == self.obj.key:
            title = 'Session {}@{} (This Session)'
        else:
            title = 'Session {}@{}'

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=title.format(self.obj.userName, self.obj.ipAddress),
            text='Session details'
        )

        form.display()

    def terminate(self):
        current_session = self.agent.si.content.sessionManager.currentSession

        if current_session.key == self.obj.key:
            self.dialog.msgbox(
                text='Cannot terminate current session'
            )
            return

        code, tag = self.dialog.yesno(
            text='Terminate session {}@{}?'.format(self.obj.userName, self.obj.ipAddress)
        )

        if code in (self.dialog.CANCEL, self.dialog.ESC):
            return

        self.dialog.infobox(
            text='Terminating session ...'
        )

        sm = self.agent.si.content.sessionManager
        sm.TerminateSession(
            sessionId=self.obj.key
        )
