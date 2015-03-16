"""
Docstring should go here

"""

import pyVmomi

from time import sleep

__all__ = ['TaskGauge']


class TaskGauge(object):
    def __init__(self, title, text, dialog, task, interval=0.5):
        """
        A task gauge displaying progress of a task

        Args:
           title               (str): Title for the gauge
           text                (str): A text to display while the gauge is running
           dialog    (dialog.Dialog): A Dialog instance
           task   (pyVmomi.vim.Task): A Task instance
           interval          (float): Check task state each 'interval' seconds

        """
        if not isinstance(task, pyVmomi.vim.Task):
            raise TypeError('Need a vim.Task instance')

        self.title = title
        self.text = text
        self.dialog = dialog
        self.task = task
        self.interval = interval

    def display(self):
        """
        docstring

        """
        self.dialog.gauge_start(
            title=self.title,
            text=self.text
        )

        while True:
            if self.task.info.state in (pyVmomi.vim.TaskInfoState.queued, pyVmomi.vim.TaskInfoState.running):
                progress = self.task.info.progress if self.task.info.progress else 0
                self.dialog.gauge_update(progress)
            elif self.task.info.state == pyVmomi.vim.TaskInfoState.success:
                break
            elif self.task.info.state == pyVmomi.vim.TaskInfoState.error:
                self.dialog.msgbox(
                    title=self.title,
                    text=self.task.info.error.msg
                )
                break
            sleep(self.interval)

        self.dialog.gauge_stop()
