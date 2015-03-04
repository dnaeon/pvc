"""
Docstring should go here

"""

from dialog import Dialog
from vconnector.core import VConnector

from pvc import __version__
from pvc.widget.menu import Menu, MenuItem
from pvc.widget.inventory import InventoryWidget

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
        welcome = 'Welcome to PVC - Python vSphere Client version {}'.format(__version__)
        self.dialog.msgbox(text=welcome, width=60)

    def login(self):
        """
        docstring

        """
        elements = [
            ('Hostname', 1, 1, '', 1, 20, 30, 40, 0),
            ('Username', 2, 1, '', 2, 20, 30, 40, 0),
            ('Password', 3, 1, '', 3, 20, 30, 40, 1)
        ]

        while True:
            code, fields = self.dialog.mixedform(
                title='Login details',
                text='Enter the IP address or DNS name of the VMware vSphere host you wish to connect to.\n',
                elements=elements,
            )

            if code in (self.dialog.CANCEL, self.dialog.ESC):
                return False

            if not all(fields):
                self.dialog.msgbox(
                    text='Invalid login details, please try again.',
                    width=45
                )
                continue

            host, user, pwd = fields
            self.dialog.infobox(
                text='Connecting to {} ...'.format(host),
                width=40
            )

            self.agent = VConnector(
                host=host,
                user=user,
                pwd=pwd
            )

            try:
                self.agent.connect()
                background_title = '{} - {} - Python vSphere Client version {}'.format(self.agent.host,
                                                                                       self.agent.si.content.about.fullName,
                                                                                       __version__)
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

        inventory = InventoryWidget(
            agent=self.agent,
            dialog=self.dialog
        )

        inventory.display()
        self.agent.disconnect()
