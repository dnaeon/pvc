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
