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
Menu Widgets

"""

__all__ = ['Menu', 'MenuItem']


class MenuItem(object):
    def __init__(self, tag, description, on_select=None, on_select_args=(), on_select_kwargs={}):
        """
        A menu item

        Args:
            tag                 (str): Unique tag name for the menu item
            description         (str): Short description of the item
            on_select      (callable): A callable to execute when the item is selected
            on_select_args    (tuple): Args to pass to the callable if the item has been selected

        """
        self.tag = tag
        self.description = description
        self.on_select = on_select
        self.on_select_args = on_select_args
        self.on_select_kwargs = on_select_kwargs

        if self.on_select and not callable(self.on_select):
            raise TypeError('Need a callable for item callback')

    def selected(self):
        return self.on_select(*self.on_select_args, **self.on_select_kwargs)


class Menu(object):
    def __init__(self, items, dialog, return_selected=False, **kwargs):
        """
        Menu class

        Args:
            items                    (list): A list of MenuItem instances
            dialog          (dialog.Dialog): A Dialog instance
            return_selected          (bool): If True them just return the selected item
            kwargs                   (dict): Additional args to be passed to dialog(1)

        """
        self.items = items
        self.dialog = dialog
        self.return_selected = return_selected
        self.kwargs = kwargs
        self.choices = [(item.tag, item.description) for item in self.items]
        self._registry = {item.tag: item for item in items}

    def display(self):
        default_item = ''
        while True:
            code, tag = self.dialog.menu(
                choices=self.choices,
                default_item=default_item,
                **self.kwargs
            )

            if code in (self.dialog.CANCEL, self.dialog.ESC):
                return code

            item = self._registry.get(tag)
            default_item = tag

            if self.return_selected:
                return item

            if item.on_select:
                item.selected()
            else:
                self.dialog.msgbox('Not implemented')
