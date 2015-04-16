# Copyright (c) 2015 Marin Atanasov Nikolov <dnaeon@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
           dialog   (dialog.Dialog): A Dialog instance
           task          (vim.Task): A Task instance
           interval         (float): Check task state each 'interval' seconds
           kwargs            (dict): Additional args to be passed to dialog(1)

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
                    text=self.task.info.error.msg
                )
                break
            sleep(self.interval)

        self.dialog.gauge_stop()
