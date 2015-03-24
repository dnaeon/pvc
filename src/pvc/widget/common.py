"""
Common Widgets Module

"""

import pvc.widget.menu
import pvc.widget.gauge
import pvc.widget.network

__all__ = ['rename']


def rename(obj, dialog, text=''):
    """
    Rename a Managed Entity

    Args:
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dialog): A Dialog instance
        text                 (str): Text to display

    """
    code, new_name = dialog.inputbox(
        title=obj.name,
        text=text,
        init=obj.name
    )

    if code in (dialog.CANCEL, dialog.ESC):
        return

    task = obj.Rename(newName=new_name)
    gauge = pvc.widget.gauge.TaskGauge(
        title=obj.name,
        text='Renaming {} to {} ...'.format(obj.name, new_name),
        dialog=dialog,
        task=task
    )

    gauge.display()

def network_menu(agent, obj, dialog, text=''):
    """
    A widget to display the networks by a Managed Entity

    Args:
        agent         (VConnector): A VConnector instance
        obj    (vim.ManagedEntity): A Managed Entity
        dialog     (dialog.Dailog): A Dialog instance
        text                 (str): Text to display

    """
    dialog.infobox(
        text='Retrieving information ...'
    )

    if not hasattr(obj, 'network'):
        dialog.msgbox(
            title=obj.name,
            text='Entity does not contain any networks'
        )
        return

    items = [
        pvc.widget.menu.MenuItem(
            tag=network.name,
            description='Accessible' if network.summary.accessible else 'Not Accessible',
            on_select=pvc.widget.network.NetworkWidget,
            on_select_args=(agent, dialog, network)
        ) for network in obj.network
    ]

    menu = pvc.widget.menu.Menu(
        title=obj.name,
        text=text,
        items=items,
        dialog=dialog
    )

    menu.display()

