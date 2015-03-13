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
            text='Retrieving message of the day ...'
        )

        sm = self.agent.si.content.sessionManager
        motd = sm.message
        motd_file = tempfile.mkstemp(prefix='pvc_motd_')

        with open(motd_file, 'w') as f:
            f.write(motd)

        code, text = self.dialog.editbox(filepath=motd_file)
        os.unlink(motd_file)

        if code == self.dialog.OK:
            self.dialog.infobox(
                text='Setting message of the day ...'
            )
            sm.UpdateServiceMessage(message=text)
