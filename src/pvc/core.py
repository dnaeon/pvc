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
Core Widgets

"""

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

import pyVmomi

import requests
requests.packages.urllib3.disable_warnings()

import pvc.widget.form
import pvc.widget.home

from dialog import Dialog
from vconnector.core import VConnector

from pvc import __version__

__all__ = ['MainApp']


class MainApp(object):
    """
    Main App class

    """
    def __init__(self):
        self.dialog = Dialog(autowidgetsize=True)
        self.dialog.add_persistent_args(['--no-mouse'])
        self.dialog.set_background_title(
            'Python vSphere Client version {}'.format(__version__)
        )
        self.agent = None

    def about(self):
        welcome = (
            'Welcome to the Python vSphere Client version {}.\n\n'
            'PVC is hosted on Github. Please contribute by reporting '
            'issues, suggesting features and sending patches using '
            'pull requests.\n\n'
            'https://github.com/dnaeon/pvc'
        )

        self.dialog.msgbox(
            title='Welcome',
            text=welcome.format(__version__)
        )

    def login(self):
        """
        Login to the VMware vSphere host

        Returns:
            True on successful connect, False otherwise

        """
        form_text = (
            'Enter IP address or DNS name '
            'of the VMware vSphere host you wish '
            'to connect to.\n'
        )

        elements = [
            pvc.widget.form.FormElement(label='Hostname'),
            pvc.widget.form.FormElement(label='Username'),
            pvc.widget.form.FormElement(label='Password', attributes=0x1),
        ]

        form = pvc.widget.form.Form(
            dialog=self.dialog,
            form_elements=elements,
            mixed_form=True,
            title='Login Details',
            text=form_text,
        )

        while True:
            code, fields = form.display()
            if code in (self.dialog.CANCEL, self.dialog.ESC):
                return False

            if not all(fields.values()):
                self.dialog.msgbox(
                    title='Error',
                    text='Invalid login details, please try again.\n'
                )
                continue

            self.dialog.infobox(
                title='Establishing Connection',
                text='Connecting to {} ...'.format(fields['Hostname']),
            )

            self.agent = VConnector(
                host=fields['Hostname'],
                user=fields['Username'],
                pwd=fields['Password'],
            )

            try:
                self.agent.connect()
                text = '{} - {} - Python vSphere Client version {}'
                background_title = text.format(
                    self.agent.host,
                    self.agent.si.content.about.fullName,
                    __version__
                )
                self.dialog.set_background_title(background_title)
                return True
            except Exception as e:
                if isinstance(e, pyVmomi.vim.MethodFault):
                    msg = e.msg
                else:
                    msg = e

                self.dialog.msgbox(
                    title='Login failed',
                    text='Failed to login to {}\n\n{}\n'.format(self.agent.host, msg)
                )

    def disconnect(self):
        """
        Disconnect from the remote vSphere host

        """
        if not self.agent:
            return

        self.dialog.infobox(
            title='Disconnecting Connection',
            text='Disconnecting from {} ...'.format(self.agent.host)
        )
        self.agent.disconnect()

    def run(self):
        try:
            self.about()
            if not self.login():
                return

            home = pvc.widget.home.HomeWidget(
                agent=self.agent,
                dialog=self.dialog
            )
            home.display()
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()
