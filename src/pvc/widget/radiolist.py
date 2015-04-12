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
Radio list widgets

"""

__all__ = ['RadioList', 'RadioListItem']


class RadioListItem(object):
    def __init__(self, tag, description='', status='off'):
        """
        A radio list item

        No more than one radio list item should be set to 'on'

        Args:
            tag         (str): Unique tag name for the item
            description (str): Short description of the item
            status      (str): Initial status of the item.
                               Using 'on' selects the item.
                               Using 'off' deselects the item.

        """
        self.tag = tag
        self.description = description
        self.status = status


class RadioList(object):
    def __init__(self, items, dialog, **kwargs):
        """
        Radio list class

        Args:
            items           (list): A list of RadioListItem instances
            dialog (dialog.Dialog): Dialog instance
            kwargs          (dict): Additional args to be passed to dialog(1)

        Returns:
            A tuple containing the code and selected tag

        """
        self.items = items
        self.dialog = dialog
        self.kwargs = kwargs
        self.choices = [(item.tag, item.description, item.status) for item in self.items]
        self._registry = {item.tag: item for item in self.items}

    def display(self):
        code, tag = self.dialog.radiolist(
            choices=self.choices,
            **self.kwargs
        )

        return (code, tag)
