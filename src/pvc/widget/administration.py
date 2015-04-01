"""
Administration module

"""

import pvc.widget.menu
import pvc.widget.session
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
                tag='Events',
                description='View Events'
            ),
            pvc.widget.menu.MenuItem(
                tag='Tasks',
                description='View Tasks'
            ),
            pvc.widget.menu.MenuItem(
                tag='Message',
                description='Message Of The Day',
                on_select=pvc.widget.motd.MOTDWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Sessions',
                description='View Sessions',
                on_select=pvc.widget.session.SessionWidget,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title='Administration',
            text='\nSelect administration item'
        )

        menu.display()
