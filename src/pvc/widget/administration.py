"""
Administration module

"""

from pvc.widget.menu import Menu, MenuItem

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
        ]

        menu = Menu(
            title='Administration',
            items=items,
            dialog=self.dialog,
            width=70,
        )
        menu.display()
