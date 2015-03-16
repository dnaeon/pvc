"""
Home Widget

"""

import pvc.widget.menu
import pvc.widget.inventory
import pvc.widget.administration

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
        sm = self.agent.si.content.sessionManager
        motd = sm.message

        if motd:
            self.dialog.msgbox(
                title='Message Of The Day',
                text=motd
            )

        items = [
            pvc.widget.menu.MenuItem(
                tag='Inventory',
                description='Inventory Menu',
                on_select=pvc.widget.inventory.InventoryWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Administration',
                description='Administration Menu',
                on_select=pvc.widget.administration.AdministrationWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title='Home',
            items=items,
            dialog=self.dialog,
            width=70
        )
        menu.display()
