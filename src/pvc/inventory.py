"""
Docstring should be here

"""

from pvc.menu import Menu, MenuItem

__all__ = ['Inventory']


class Inventory(object):
    def __init__(self, agent, dialog):
        """
        Inventory menu

        Args:
            agent (VConnector): A VConnector instance
            dialog    (Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog

    def menu(self):
        items = [
            MenuItem(
                tag='Hosts and Clusters',
                description='Manage hosts and clusters',
            ),
            MenuItem(
                tag='VMs and Templates',
                description='Manage VMs and templates'
            ),
            MenuItem(
                tag='Datastores',
                description='Manage Datastores and Datastore Clusters'
            ),
            MenuItem(
                tag='Networking',
                description='Manage Networking'
            ),
        ]

        menu = Menu(
            text='Inventory Menu',
            items=items,
            dialog=self.dialog
        )
        menu.display()
