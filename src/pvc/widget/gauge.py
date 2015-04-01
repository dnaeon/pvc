"""
Gauge Widgets

"""

import pyVmomi

from time import sleep

__all__ = ['TaskGauge']


class TaskGauge(object):
    def __init__(self, dialog, task, interval=0.5, **kwargs):
        """
        A gauge for displaying progress of a task

        Args:
           dialog    (dialog.Dialog): A Dialog instance
           task   (pyVmomi.vim.Task): A Task instance
           interval          (float): Check task state each 'interval' seconds
           kwargs             (dict): Additional args to be passed to dialog(1)

        """
        self.dialog = dialog
        self.task = task
        self.interval = interval
        self.kwargs = kwargs

    def display(self):
        """
        docstring

        """
        self.dialog.gauge_start(
            **self.kwargs
        )

        while True:
            if self.task.info.state in (pyVmomi.vim.TaskInfoState.queued, pyVmomi.vim.TaskInfoState.running):
                progress = self.task.info.progress if self.task.info.progress else 0
                self.dialog.gauge_update(progress)
            elif self.task.info.state == pyVmomi.vim.TaskInfoState.success:
                break
            elif self.task.info.state == pyVmomi.vim.TaskInfoState.error:
                self.dialog.msgbox(
                    title='Task Error',
                    text=self.task.info.error.msg,
                    width=60
                )
                break
            sleep(self.interval)

        self.dialog.gauge_stop()
