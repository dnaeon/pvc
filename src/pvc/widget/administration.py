"""
Administration module

"""

import pvc.widget.common
import pvc.widget.menu
import pvc.widget.motd

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
            pvc.widget.menu.MenuItem(
                tag='Message',
                description='Message Of The Day',
                on_select=pvc.widget.motd.MOTDWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Sessions',
                description='View Sessions',
                on_select=pvc.widget.common.session_menu,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Administration',
            text='Select administration item'
        )

        menu.display()
