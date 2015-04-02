"""
Session module

"""

import pyVmomi

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
            title='Confirmation',
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
