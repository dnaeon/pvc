"""
Network Widget module

"""

import pvc.widget.event
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.common
import pvc.widget.virtualmachine

__all__ = ['NetworkWidget']


class NetworkWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Network Widget

        Args:
            agent     (VConnector): A VConnector instance
            dialog (dialog.Dialog): A Dialog instance
            obj      (vim.Network): A vim.Network managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Summary',
                description='General Information',
                on_select=self.summary
            ),
            pvc.widget.menu.MenuItem(
                tag='Virtual Machines',
                description='Virtual Machines using this network',
                on_select=pvc.widget.common.virtual_machine_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Hosts',
                description='Hosts using this network',
                on_select=pvc.widget.common.host_menu,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
            pvc.widget.menu.MenuItem(
                tag='Tasks',
                description='View Tasks',
            ),
            pvc.widget.menu.MenuItem(
                tag='Events',
                description='View Events',
                on_select=pvc.widget.event.EventWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select item from menu'
        )

        menu.display()

    def summary(self):
        """
        General information about the network

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Name',
                item=self.obj.name
            ),
            pvc.widget.form.FormElement(
                label='Accessible',
                item=str(self.obj.summary.accessible)
            ),
            pvc.widget.form.FormElement(
                label='IP Pool',
                item=self.obj.summary.ipPoolName
            ),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='Network summary information'
        )

        form.display()
