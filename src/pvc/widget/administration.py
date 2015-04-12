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
Administration module

"""

import pvc.widget.common
import pvc.widget.menu
import pvc.widget.motd

__all__ = ['AdministrationWidget']


class AdministrationWidget(object):
    def __init__(self, agent, dialog):
        """
        Administration widget

        Args:
            agent (VConnector): A VConnector instance
            dialog    (Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog
        self.title = 'Administration'
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Message',
                description='Message Of The Day',
                on_select=pvc.widget.motd.MOTDWidget,
                on_select_args=(self.agent, self.dialog)
            ),
            pvc.widget.menu.MenuItem(
                tag='Sessions',
                description='View Sessions',
                on_select=pvc.widget.common.session_menu,
                on_select_args=(self.agent, self.dialog)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an action to be performed'
        )

        menu.display()
