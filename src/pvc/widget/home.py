"""
Home Widget

"""


from pvc.widget.menu import Menu, MenuItem
from pvc.widget.inventory import InventoryWidget
from pvc.widget.administration import AdministrationWidget

__all__ = ['HomeWidget']


class HomeWidget(object):
    def __init__(self, agent, dialog):
        """
        Home widget

        Args:
            agent (VConnector): A VConnector instance
            dialog    (Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog

    def display(self):
        items = [
            MenuItem(
                tag='Inventory',
                description='Inventory Menu',
                on_select=InventoryWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            MenuItem(
                tag='Administration',
                description='Administration Menu',
                on_select=AdministrationWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = Menu(
            title='Home',
            items=items,
            dialog=self.dialog,
            width=70
        )
        menu.display()
