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
        self.warn_if_not_vcenter()
        self.show_motd()

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
            items=items,
            dialog=self.dialog,
            title='Home',
            text='Select an item from menu',
            cancel_label='Logout'
        )

        menu.display()

    def warn_if_not_vcenter(self):
        about = self.agent.si.content.about

        if about.apiType == 'VirtualCenter':
            return

        text = (
            'You are currently connected to a {} system.\n\n'
            'Some of the features provided by PVC may or may not '
            'be available for the host to which you are currently '
            'connected.\n\n'
            'In order to take full advantage of all PVC '
            'features you should disconnect now and connect to a '
            'VMware vCenter server managing this host.'
        )

        self.dialog.msgbox(
            title='Warning',
            text=text.format(about.fullName)
        )

        view = self.agent.get_host_view()
        host = view.view[0]
        management_ip = host.summary.managementServerIp
        view.DestroyView()

        if management_ip:
            text = (
                'This host is currently being managed by the '
                'VMware vCenter server with IP address {0}.\n\n'
                'You should disconnect now and connect to the '
                'VMware vCenter server at {0}.\n'
            )
            self.dialog.msgbox(
                title='Warning',
                text=text.format(management_ip)
            )

    def show_motd(self):
        sm = self.agent.si.content.sessionManager
        motd = sm.message

        if motd:
            self.dialog.msgbox(
                title='Message Of The Day',
                text=motd
            )
