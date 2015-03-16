"""
Session module

"""

import pyVmomi
import pvc.widget.menu
import pvc.widget.form

__all__ = ['SessionWidget']


class SessionWidget(object):
    def __init__(self, agent, dialog):
        """
        Session Widget

        Args:
            agent     (VConnector): A VConnector instance
            dialog (dialog.Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog
        self.display()

    def display(self):
        self.dialog.infobox(
            text='Retrieving Sessions ...'
        )

        try:
            sm = self.agent.si.content.sessionManager
            session_list = sm.sessionList
        except pyVmomi.vim.NoPermission:
            self.dialog.msgbox(
                title='Access Denied',
                text='No permissions to view sessions'
            )
            return

        items = [
            pvc.widget.menu.MenuItem(
                tag=session.key,
                description='{}@{}'.format(session.userName, session.ipAddress),
                on_select=self.session_menu,
                on_select_args=(session,)
            ) for session in session_list
        ]

        menu = pvc.widget.menu.Menu(
            title='Sessions',
            text='Select a session for more detais',
            items=items,
            dialog=self.dialog,
            width=70
        )
        menu.display()

    def session_menu(self, session):
        """
        User session menu

        Args:
            session (vim.UserSession): A vim.UserSession instance

        """
        items = [
            pvc.widget.menu.MenuItem(
                tag='Details',
                description='View Session Details',
                on_select=self.details,
                on_select_args=(session,)
            ),
            pvc.widget.menu.MenuItem(
                tag='Terminate',
                description='Terminate Session',
                on_select=self.terminate,
                on_select_args=(session,)
            ),
        ]

        current_session = self.agent.si.content.sessionManager.currentSession
        if current_session.key == session.key:
            title = 'Session {}@{} (This Session)'
        else:
            title = 'Session {}@{}'

        menu = pvc.widget.menu.Menu(
            title=title.format(session.userName, session.ipAddress),
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def details(self, session):
        """
        View details about a user session

        Args:
            session (vim.UserSession): A vim.UserSession instance

        """
        self.dialog.infobox(
            text='Retrieving Session Details ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Username',
                item=session.userName
            ),
            pvc.widget.form.FormElement(
                label='Full Name',
                item=session.fullName
            ),
            pvc.widget.form.FormElement(
                label='Login Time',
                item=str(session.loginTime)
            ),
            pvc.widget.form.FormElement(
                label='Last Active',
                item=str(session.lastActiveTime)
            ),
            pvc.widget.form.FormElement(
                label='Idle',
                item=str(self.agent.si.CurrentTime() - session.lastActiveTime)
            ),
            pvc.widget.form.FormElement(
                label='IP Address',
                item=session.ipAddress
            ),
            pvc.widget.form.FormElement(
                label='User Agent',
                item=session.userAgent
            ),
            pvc.widget.form.FormElement(
                label='API Invocations',
                item=str(session.callCount)
            ),
        ]

        current_session = self.agent.si.content.sessionManager.currentSession
        if current_session.key == session.key:
            title = 'Session {}@{} (This Session)'
        else:
            title = 'Session {}@{}'

        form = pvc.widget.form.Form(
            title=title.format(session.userName, session.ipAddress),
            dialog=self.dialog,
            form_elements=elements
        )
        form.display()

    def terminate(self, session):
        """
        Terminate a user session

        Args:
            session (vim.UserSession): A vim.UserSession instance

        """
        current_session = self.agent.si.content.sessionManager.currentSession

        if current_session.key == session.key:
            self.dialog.msgbox(
                text='Cannot terminate current session'
            )
            return

        self.dialog.infobox(
            text='Terminating session ...'
        )

        sm = self.agent.si.content.sessionManager
        sm.TerminateSession(
            sessionId=session.key
        )
