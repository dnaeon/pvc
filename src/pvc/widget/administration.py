"""
Administration module

"""

from pvc.widget.menu import Menu, MenuItem
from pvc.widget.session import SessionWidget
from pvc.widget.motd import MOTDWidget

__all__ = ['AdministrationWidget']


class AdministrationWidget(object):
    def __init__(self, agent, dialog):
        """
        Administration widget

        Args:
            agent (VConnector): A VConnector instance
            dialog    (Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog
        self.display()

    def display(self):
        items = [
            MenuItem(
                tag='Events',
                description='View Events'
            ),
            MenuItem(
                tag='Tasks',
                description='View Tasks'
            ),
            MenuItem(
                tag='Message',
                description='Message Of The Day',
                on_select=MOTDWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            MenuItem(
                tag='Sessions',
                description='View Sessions',
                on_select=SessionWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = Menu(
            title='Administration',
            items=items,
            dialog=self.dialog,
            width=70,
        )
        menu.display()
