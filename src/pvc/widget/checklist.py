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
    def __init__(self, items, dialog, **kwargs):
        """
        CheckList class

        Args:
            items           (list): List of CheckListItem instances
            dialog (dialog.Dialog): Dialog instance
            kwargs          (dict): Additional args to be passed to dialog(1)

        """
        self.items = items
        self.dialog = dialog
        self.kwargs = kwargs
        self.choices = [(item.tag, item.description, item.status) for item in self.items]
        self._registry = {item.tag: item for item in self.items}

    def display(self):
        code, tags = self.dialog.checklist(
            choices=self.choices,
            **self.kwargs
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
