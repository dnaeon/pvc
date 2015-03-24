"""
Common Widgets Module

"""

import pvc.widget.gauge

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

    if code in (self.dialog.CANCEL, self.dialog.ESC):
        return

    task = obj.Rename(newName=new_name)
    gauge = pvc.widget.gauge.TaskGauge(
        title=obj.name,
        text='Renaming {} to {} ...'.format(obj.name, new_name),
        dialog=dialog,
        task=task
    )

    gauge.display()
