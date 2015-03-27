"""
Docstring should go here

"""

import requests
requests.packages.urllib3.disable_warnings()

from dialog import Dialog
from vconnector.core import VConnector

from pvc import __version__
from pvc.widget.form import Form, FormElement
from pvc.widget.menu import Menu, MenuItem
from pvc.widget.home import HomeWidget

__all__ = ['MainApp']


class MainApp(object):
    """
    docstring

    """
    def __init__(self):
        """
        docstring

        """
        self.dialog = Dialog()
        self.dialog.set_background_title(
            'Python vSphere Client version {}'.format(__version__)
        )
        self.agent = None

    def about(self):
        welcome = (
            'Welcome to the Python vSphere Client version {}.\n\n'
            'PVC is hosted on Github. Please contribute by reporting '
            'issues, suggesting features and sending patches using '
            'pull requests.\n\n'
            'https://github.com/dnaeon/pvc'
        )

        text = welcome.format(__version__)
        self.dialog.msgbox(text=text, height=15, width=60)

    def login(self):
        """
        docstring

        """
        form_text = (
            'Enter IP address or DNS name '
            'of the vSphere host you wish '
            'to connect to.\n'
        )
        form_elements = [
            FormElement(label='Hostname'),
            FormElement(label='Username'),
            FormElement(label='Password', attributes=0x1),
        ]
        form = Form(
            dialog=self.dialog,
            form_elements=form_elements,
            title='Login details',
            text=form_text,
            mixed_form=True
        )

        while True:
            code, fields = form.display()
            if code in (self.dialog.CANCEL, self.dialog.ESC):
                return False

            if not all(fields.values()):
                self.dialog.msgbox(
                    text='Invalid login details, please try again.',
                    width=45
                )
                continue

            self.dialog.infobox(
                text='Connecting to {} ...'.format(fields['Hostname']),
                width=40
            )

            self.agent = VConnector(
                host=fields['Hostname'],
                user=fields['Username'],
                pwd=fields['Password'],
            )

            try:
                self.agent.connect()
                text = '{} - {} - Python vSphere Client version {}'
                background_title = text.format(
                    self.agent.host,
                    self.agent.si.content.about.fullName,
                    __version__
                )
                self.dialog.set_background_title(background_title)
                return True
            except Exception as e:
                self.dialog.msgbox(
                    title='Login failed',
                    text='Failed to login to {}\n\n{}\n'.format(self.agent.host, e.msg),
                    width=40
                )

    def run(self):
        """
        docstring

        """
        self.about()
        if not self.login():
            return

        home = HomeWidget(
            agent=self.agent,
            dialog=self.dialog
        )
        home.display()

        self.dialog.infobox(
            text='Disconnecting from {} ...'.format(self.agent.host)
        )
        self.agent.disconnect()
