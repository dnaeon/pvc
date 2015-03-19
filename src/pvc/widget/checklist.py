"""
Check list widgets

"""

__all__ = ['CheckList', 'CheckListItem']


class CheckListItem(object):
    def __init__(self, tag, description='', status='off'):
        """
        A menu item

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

    def on(self):
        self.status = 'on'

    def off(self):
        self.status = 'off'

    def is_on(self):
        return self.status == 'on'

    def is_off(self):
        return self.status == 'off'


class CheckList(object):
    def __init__(self, items, dialog, title='', text='', height=0, width=0):
        """
        CheckList class

        Args:
            items           (list): List of CheckListItem instances
            dialog (dialog.Dialog): Dialog instance
            title            (str): Title for the box
            text             (str): Text to display
            height           (int): Height of the box
            width            (int): Width of the box

        """
        self.text = text
        self.title = title
        self.items = items
        self.dialog = dialog
        self.height = height
        self.width = width
        self.choices = [(item.tag, item.description, item.status) for item in self.items]
        self._registry = {item.tag: item for item in self.items}

    def display(self):
        code, tags = self.dialog.checklist(
            title=self.title,
            text=self.text,
            choices=self.choices,
            height=self.height,
            width=self.width
        )

        selected = tags
        deselected = set(self._registry.keys() - selected)

        for item in selected:
            self._registry[item].on()
        for item in deselected:
            self._registry[item].off()

    def selected(self):
        """
        Returns a list of the selected items

        """
        return [item.tag for item in self.items if item.is_on()]

    def deselected(self):
        """
        Returns a list of the deselected items

        """
        return [item.tag for item in self.items if item.is_off()]
