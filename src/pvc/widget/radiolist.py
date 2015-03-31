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
    def __init__(self, items, dialog, title='', text='', height=0, width=0):
        """
        Radio list class

        Args:
            items           (list): A list of RadioListItem instances
            dialog (dialog.Dialog): Dialog instance
            title            (str): Title for the box
            text             (str): Text to display
            height           (int): Height of the box
            width            (int): Width of the box

        Returns:
            A tuple containing the code and selected tag

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
        code, tag = self.dialog.radiolist(
            title=self.title,
            text=self.text,
            choices=self.choices,
            height=self.height,
            width=self.width
        )

        return (code, tag)
