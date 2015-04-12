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
Message Of The Day module

"""

import os
import tempfile

__all__ = ['MOTDWidget']


class MOTDWidget(object):
    def __init__(self, agent, dialog):
        """
        Message Of The Day Widget

        Args:
            agent     (VConnector): A VConnector instance
            dialog (dialog.Dialog): A Dialog instance

        """
        self.agent = agent
        self.dialog = dialog
        self.display()

    def display(self):
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        sm = self.agent.si.content.sessionManager
        motd = sm.message + '\n'
        fd, motd_file = tempfile.mkstemp(prefix='pvc_motd_')

        with open(motd_file, 'w') as f:
            f.write(motd)

        code, text = self.dialog.editbox(
            title='Message Of The Day',
            filepath=motd_file
        )
        os.unlink(motd_file)

        if code == self.dialog.OK:
            self.dialog.infobox(
                text='Setting message of the day ...'
            )
            sm.UpdateServiceMessage(message=text.rstrip())
